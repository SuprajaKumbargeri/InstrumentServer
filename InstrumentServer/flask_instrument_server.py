import sys
import os
import logging
import datetime
import threading
from PyQt6.QtWidgets import *
from flask import (Flask, render_template)

import InstrumentDetection.instrument_detection_service as ids
from DB import db
import serverStatus
import driverParser
import instrumentDB
import InstrumentServerGui as gui


###################################################################################
# FlaskInstrumentServer
###################################################################################
class FlaskInstrumentServer:

    def __init__(self, dev_mode=False):
        """Initializes Instrument Server Application"""
        self._my_logger = self.setup_logger()
        self._dev_mode = dev_mode
        self._flask_app = self.create_app()

    def run_server(self, host='127.0.0.1', port=5000, threaded=True):
        """Deploys Instrument Server Application"""

        # Start GUI on a different thread and run in the background (daemon)
        gui_thread = threading.Thread(target=self.start_instrument_server_gui, args=[], daemon=True)
        gui_thread.start()

        self._flask_app.run(host=host, port=port, threaded=threaded)

    def get_logger(self):
        """Get the application logger"""
        return self._my_logger

    def setup_logger(self):
        """Setup the Logger"""
        my_logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        my_logger.addHandler(handler)
        my_logger.setLevel(logging.DEBUG)
        return my_logger

    def start_instrument_server_gui(self):
        self.get_logger().debug(f'Instrument Server GUI thread ID: {threading.get_native_id()}')
        app = QApplication(sys.argv)
        main_win = gui.InstrumentServerWindow(self._flask_app, self.get_logger(), dev_mode=self._dev_mode)
        main_win.resize(800, 600)
        main_win.show()
        app.exec()

    def create_app(self, test_config=None):
        """Creates Instrument Server Flask Application"""

        self.get_logger().debug(f'Creating Flask App Thread ID: {threading.get_native_id()}')

        instrument_detection_service = ids.InstrumentDetectionService(self._my_logger)

        # Delegate Instrument detection to a separate thread
        detect_inst_thread = None
        if not self._dev_mode:
            detect_inst_thread = threading.Thread(target=instrument_detection_service.detectInstruments())
            detect_inst_thread.start()

        # Configure PostgreSQL instance to start and stop with the Instrument Server
        # Commented during development phase
        '''
        status = os.system('cmd /c "pg_ctl -D "C:\Program Files\PostgreSQL\\15\data" start"')
        if status == 1:
            my_logger.error("Failed to start PostgreSQL Server. Shutting down Instrument Server.")
            sys.exit("Failed to start PostgreSQL Server. Shutting down Instrument Server.")
        '''

        # create and configure instrument server
        # __name__ is the name of the current Python module
        # instance_relative_config tells app that config file is
        # relatie to insance folder
        self.get_logger().info(f'Creating Flask application: {__name__}')

        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(SECRET_KEY='dev', DATABASE='postgres://postgres:1234@localhost/instrument_db')
        app.config['JSON_SORT_KEYS'] = False

        if test_config is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile('config.py', silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)

        # Ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # Register database application
        if not self._dev_mode:
            db.setLogger(self._my_logger)
            db.init_db(app)

        # Register Server Status blueprint
        app.register_blueprint(serverStatus.bp)
        serverStatus.set_Logger(self._my_logger)

        app.register_blueprint(driverParser.bp)
        driverParser.setLogger(self._my_logger)

        # Wait for Instrument detection to finish
        if not self._dev_mode:
            detect_inst_thread.join()

        # Register instrument database related blueprint
        app.register_blueprint(instrumentDB.bp)
        instrumentDB.setLogger(self._my_logger)

        # Main route
        @app.route('/')
        def index():
            """The main route for Instrument Server"""
            return render_template("index.html", utc_date=datetime.datetime.utcnow())

        @app.route('/shutDown')
        def shut_down():
            # os.system('cmd /c "pg_ctl -D "C:\Program Files\PostgreSQL\\15\data" stop"')
            self._my_logger.info("Instrument Server is shutting down...")

            # Terminate the entire application
            os._exit(0)

        return app
