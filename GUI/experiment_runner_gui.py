import os
import sys
from time import sleep
import logging

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from datetime import datetime

###################################################################################
# StringParameter
###################################################################################
class StringParameter(Parameter):
    """ :class:`Parameter` sub-class that uses the string type to store the value.

    :var value: The string value of the parameter
    :param name: The parameter name
    :param default: The default string value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    @property
    def value(self):
        if self.is_set():
            return self._value
        else:
            return ''

    @value.setter
    def value(self, value):
        self._value = str(value)


###################################################################################
# MainExperimentProcedure
###################################################################################
class MainExperimentProcedure(Procedure):
    steps = IntegerParameter('Steps', default=50000)
    sigma = FloatParameter('Sigma', default=10.0)
    beta = FloatParameter('Beta', default=3.0)
    rho = FloatParameter('Rho', default=28.0)
    comments = StringParameter('Comments', default='No comments')

    def set_logger(self, logger: logging.Logger):
        self.logger = logger

    #
    # The columns in the plotter
    #
    DATA_COLUMNS = ['step', 'x', 'y', 'z']

    def startup(self):
        self.logger.info('startup() was called')

    # Sample Data Generation...
    def execute(self):
        self.logger.info(f'Starting experiment loop of {self.steps} steps')

        x = 1.0
        y = 1.0
        z = 1.0
        dx = 0
        dy = 0
        dz = 0
        dt = 0.001

        #
        # Main experiment LOOP
        #
        for i in range(int(self.steps)):

            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z

            x += dt * dx
            y += dt * dy
            z += dt * dz

            # The datapoints we record at each "step":
            data = {
                'step': int(i),
                'x': x,
                'y': y,
                'z': z
            }

            self.emit('results', data)
            self.logger.debug(f'Emitting results: {data}')
            self.emit('progress', 100 * i / self.steps)

            # Intentional sleep to simulate "live plotting"
            sleep(0.00001)

            if self.should_stop():
                self.logger.warning("Caught the stop flag in the procedure")
                break


###################################################################################
# MainExperimentWindow
###################################################################################
class ExperimentRunner(ManagedWindow):

    def __init__(self, parent_gui, logger: logging.Logger, base_filename='experiment_results'):
        # Initialize the super class
        super().__init__(procedure_class=MainExperimentProcedure,
                         inputs=['steps', 'sigma', 'beta', 'rho', 'comments'],  # Inputs
                         displays=['steps', 'sigma', 'beta', 'rho', 'comments'],  # Display GUI textboxes
                         x_axis='x',
                         y_axis='y',
                         directory_input=True)  # Enables directory input widget

        # A reference to the invoking GUI
        self.parent_gui = parent_gui

        play_icon = QIcon("../Icons/playButton.png")
        self.setWindowIcon(play_icon)

        # The logger
        self.logger = logger

        self.base_filename = base_filename
        self.setWindowTitle('Experiment Runner')
        self.directory = os.path.dirname(os.path.realpath(__file__))

        # Constructs the file menu up top
        self.construct_menu_bar()

        # This is the outermost widget or the "main" widget
        self.main_widget = self.main
        self.main_layout = self.main_widget.layout()

        quit_btn = QtWidgets.QPushButton('Quit', self)
        quit_btn.clicked.connect(self.exit_gui)

        self.main_layout.addWidget(quit_btn)
        self.main_layout.setAlignment(quit_btn, Qt.AlignmentFlag.AlignRight)

    def queue(self, procedure=None):
        self.logger.info('Starting measurement procedure')

        # The full path to file where the experiment results will be written to
        filename = os.path.join(self.directory, self.generate_experiment_file_name(self.base_filename))
        self.logger.info(f'Writing results to file {filename}')

        if procedure is None:
            procedure = self.make_procedure()
            procedure.set_logger(self.logger)

        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)

    def generate_experiment_file_name(self, base_name: str):
        """
        Generates the experiment filename (.txt) with appended system time timestamp
        ex: <base_name>_2023_03_19-01_51_06_PM_.txt
        """
        timestamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        return f'{base_name}_{timestamp}_.txt'

    def construct_menu_bar(self):
        """
        Constructs the Menu Bar on top
        """
        experiment_menu_bar = self.menuBar()
        experiment_menu_bar.addSeparator()
        file_menu = experiment_menu_bar.addMenu("&File")

        # Defines the action to exit GUI via the menu bar File section
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.exit_gui)
        file_menu.addAction(exit_action)

        help_menu = experiment_menu_bar.addMenu("&Help")

    def exit_gui(self):
        """
        Closes the experiment GUI
        """
        self.close()


if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    app = QtWidgets.QApplication(sys.argv)
    window = ExperimentRunner(None, logger)
    window.show()
    sys.exit(app.exec())
