###################################################################################
# Instrument Server
###################################################################################

import sys
import os
import logging
import datetime
import threading
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from flask import (Flask, jsonify, render_template)

'''
SetUp Logger
'''
def setup_logger():
    global my_logger 
    my_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    my_logger.setLevel(logging.INFO)



def start_gui():
    print('GUI thread ID: {}'.format(threading.get_native_id()))
    from . import InstrumentServerGui as gui
    app = QApplication(sys.argv)
    mainWin = gui.InstrumentServerWindow()
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(800, 600)
    mainWin.show()
    app.exec()


'''
Create the Flask Application
'''
# Application Factory 
def create_app(test_config=None):

    setup_logger()
    from . InstrumentDetection import instrument_detection_service as ids
    instrumentDetectionServ = ids.InstrumentDetectionService(my_logger)

    # Delegate Instrument dectection to a separate thread
    detectInstTh = threading.Thread(target=instrumentDetectionServ.detectInstruments())
    detectInstTh.start()

    # create and configure instrument server
    # __name__ is the name of the current Python module
    # instance_relative_config tells app that config file is 
    # relatie to insance folder
    my_logger.info('Creating Flask application: {}'.format(__name__))

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
    from . import db
    db.setLogger(my_logger)
    db.init_db(app)

    # Register Server Status blueprint
    from . import serverStatus
    app.register_blueprint(serverStatus.bp)
    serverStatus.set_Logger(my_logger)

    from . import driverParser
    app.register_blueprint(driverParser.bp)
    driverParser.setLogger(my_logger)

    # Wait for Instrument dectection to finish 
    detectInstTh.join()

    from . InstrumentCom import instrument_com
    app.register_blueprint(instrument_com.bp)
    instrument_com.initialize(my_logger, instrumentDetectionServ.get_visa_instruments(), instrumentDetectionServ.get_pico_instruments())

    # Register instrument database related blueprint
    from . import instrumentDB
    app.register_blueprint(instrumentDB.bp)
    instrumentDB.setLogger(my_logger)

    print('Create Flask App Thread ID: {}'.format(threading.get_native_id()))

    # Start GUI on a different thread and run in the background (daemon)
    guiThread = threading.Thread(target=start_gui, daemon=True)
    guiThread.start()

    # Main route
    @app.route('/')
    def index():
        return render_template("index.html", utc_date=datetime.datetime.utcnow())

    @app.route('/shutDown')
    def shutDown():
        instrument_com.closeAllInstruments()
        my_logger.info("Instrumer Server is shutting down...")

        # Terminate the entire application
        os._exit(0)

    return app
