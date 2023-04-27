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

from itertools import product
import numpy as np
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
    # datapoints = IntegerParameter('datapoints', default=1)
    # start = FloatParameter('start', units='V', default=1)
    # stop = FloatParameter('stop', units='V', default=2)
    # TODO: Create dynamic paremeters if needed
    
    input = []
    output = []
    sequence = {}
    quantities = {}
    input_quantity_managers = []
    output_quantity_managers = []
    
    def set_logger(self, logger: logging.Logger):
        self.logger = logger

    #
    # The columns in the plotter
    #
    DATA_COLUMNS = ['step', 'step2']
    input_data_names = {}
    output_data_names = {}

    def startup(self):
        self.logger.info('startup() was called')
        
        # if self.instruments:
        #     self.ins_a = self.instruments['Instrument D'].quantities['Offset']
        #     self.ins_b = self.instruments['Instrument B'].quantities['Offset']
        # else:
        #     self.logger.warning("Error finding instrument managers")
        #     # TODO: Stop execution
        #     self.shutdown()

    def generate_sequence(self, seq: dict):
        if seq['datatype'].upper() == 'DOUBLE':
            return np.linspace(seq['start'], seq['stop'], seq['datapoints'])
        else:
            if seq['start'] != seq['stop']:
                number_of_points = seq['datapoints']
                return ([seq['start']] * (number_of_points // 2)) + ([seq['stop']] * (number_of_points - (number_of_points // 2)))
            else:
                return [seq['start']] * seq['datapoints']
            
    def set_parameters(self, inputs=None, outputs=None):
        for level in self.input:
            for instrument_name, quantity_name in level:
                input_name = "Input - " + str(instrument_name) + " - " + str(quantity_name)
                if input_name not in self.DATA_COLUMNS:
                    self.DATA_COLUMNS.append(input_name)
                    self.input_data_names[(instrument_name, quantity_name)] = input_name
        for instrument_name, quantity_name in self.output:
            output_name = "Output - " + str(instrument_name) + " - " + str(quantity_name)
            if output_name not in self.DATA_COLUMNS:
                self.DATA_COLUMNS.append(output_name)
                self.output_data_names[instrument_name, quantity_name] = output_name



    # Sample Data Generation...
    def execute(self):
        self.logger.info(f'Starting experiment loop of {"###"} steps') # TODO: Remove
        #
        # Main experiment LOOP
        #

        datapoints = 1 # number of datapoints
        individual_sequences = []
        for level in self.input:
            sequences_in_level = []
            for (ins, qty) in level:
                sequence = self.generate_sequence(self.sequence[(ins, qty)])
                sequences_in_level.append(sequence)
                if len(sequence) == 0:
                    # TODO: handle error
                    pass
            datapoints *= len(sequences_in_level[0])
            """
            converting [[1, 2, 3], ['a', 'b', 'c']] to [(1, 'a'), (2, 'b'), (3, 'c')]
            """
            sequences_in_order = list(zip(*sequences_in_level))
            individual_sequences.append(sequences_in_order)        
        
        combined_sequences = product(*individual_sequences)

        sleep_time = 0.001
        step = 0

        for step_sequence in combined_sequences:
            # step sequence is a list of tupules [(1 , 'a'), (True, )]
            # The datapoints we record at each "step":
            print(step_sequence)     
            data = {}
            for level in range(len(self.input)):
                for index in range(len(self.input[level])):
                    (ins, qty) = self.input[level][index]                
                    self.quantities[(ins, qty)].set_value(step_sequence[level][index])
                    data[self.input_data_names[(ins, qty)]] = step_sequence[level][index]
                    sleep(sleep_time)                

            for (ins, qty) in self.output:
                data[self.output_data_names[(ins, qty)]] = self.quantities[(ins, qty)].get_value()
                sleep(sleep_time)

            data['step'] = step
            self.logger.info("Data point recorded: ", data)
            self.emit('results', data)
            self.logger.debug(f'Emitting results: {data}')
            self.emit('progress', 100 * step / datapoints)

            # Intentional sleep to simulate "live plotting"
            sleep(0.00001)
            step += 1
                

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
                         x_axis='step',
                         y_axis='step',
                         directory_input=True)  # Enables directory input widget
        # self.set_parameters(params)       

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

    def set_parameters(self, parameters):
        self.logger.info('Setting parameter values')
        return super().set_parameters(parameters)

    def queue(self, procedure=None):
        self.logger.info('Starting measurement procedure')

        # The full path to file where the experiment results will be written to
        filename = os.path.join(self.directory, self.generate_experiment_file_name(self.base_filename))
        self.logger.info(f'Writing results to file {filename}')

        #if procedure is None:
            # procedure = self.make_procedure()
        procedure = MainExperimentProcedure()
        procedure.set_logger(self.logger)
        
        # might be moved to startup
        '''
        procedure.quantities = {('Instrument B', 'Offset'): self.parent_gui._working_instruments['Instrument B'].quantities['Offset'],
                                ('Instrument D', 'Offset'): self.parent_gui._working_instruments['Instrument D'].quantities['Offset'],
                                ('Instrument B', 'Output load'): self.parent_gui._working_instruments['Instrument B'].quantities['Output load'],
                                ('Instrument D', 'Output load'): self.parent_gui._working_instruments['Instrument D'].quantities['Output load'],
                                ('Instrument B', 'Output trigger'): self.parent_gui._working_instruments['Instrument B'].quantities['Output trigger'],
                                ('Instrument D', 'Output trigger'): self.parent_gui._working_instruments['Instrument D'].quantities['Output trigger']                                  
                                }
        procedure.sequence = { ('Instrument D', 'Offset'): { 'datapoints': 3, 'start': -2.0, 'stop': 2.0, 'datatype': 'DOUBLE'},
                                ('Instrument D', 'Output load'): { 'datapoints': 3, 'start': '10 kOhm', 'stop': '50 Ohm', 'datatype': 'COMBO'},
                                ('Instrument D', 'Output trigger'): { 'datapoints': 1, 'start': 'True', 'stop': 'True', 'datatype': 'BOOLEAN'}}
        # self.parent_gui.sequence
        procedure.input = [[('Instrument D', 'Offset'), ('Instrument D', 'Output load')], [('Instrument D', 'Output trigger')]]
        procedure.output = [('Instrument B', 'Offset'), ('Instrument B', 'Output load'), ('Instrument B', 'Output trigger')]
        '''
        procedure.input = self.parent_gui.input_DTO
        procedure.sequence = self.parent_gui.sequence_DTO
        procedure.output = self.parent_gui.output_DTO
        procedure.quantities = self.parent_gui.quantities_DTO
        
        procedure.set_parameters()

        # params = {'datapoints': 9, 'start': -4.0, 'stop': 4.0}
        # procedure.set_parameters(params, except_missing=False)
        

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
