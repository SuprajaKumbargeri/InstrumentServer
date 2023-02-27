from enum import Enum
from pyvisa import *
import requests


# Maps terminating character from ini File to actual character
TERM_CHAR = Enum('TERM_CHAR',
                 {'Auto': 'Auto',
                  'None': '',
                  'CR': '\r',
                  'LF': '\n',
                  'CR+LF': '\r\n'})

###################################################################################
# InstrumentManager
###################################################################################
class InstrumentManager:
    def __init__(self, name, connection):
        self._name = name
        self._instrument = None
        self._driver = None
        self._timeout = 1000.0
        self._term_chars = None
        self._send_end = None
        self._baud_rate = None
        self._data_bits = None
        self._stop_bits = None
        self._parity = None

        # Get the driver dictionary
        self._get_driver()
        self._initialize_visa_settings()

        if self._is_serial_instrument():
            self._get_serial_values()

        self._initialize_instrument(connection)

        # TODO: add check for visa instrument

        # checks if model is correct, throws error if not
        self._check_model()

        #self._startup()

    def _get_driver(self):
        """Communicates with instrument server to get driver for instrument"""
        # implementation will likely change
        url = r'http://127.0.0.1:5000/instrumentDB/getInstrument'
        response = requests.get(url, params={'cute_name': self._name})

        if 300 > response.status_code >= 200:
            self._driver = dict(response.json())
        else:
            response.raise_for_status()

    def _initialize_instrument(self, connection):
        """Initializes PyVISA resource if a PyVISA resource string was given at construction"""
        # string passed through in VISA form
        if isinstance(connection, str):
            self._rm = ResourceManager()

            if self._is_serial_instrument():
                # The actual terminating chars as str
                read_term = str(TERM_CHAR[self._term_chars].value)

                print('Using the following parameters to connect to serial VISA instrument: resource_name={}, '
                      'read_termination={}, baud_rate={}'.format(connection,
                                                                 TERM_CHAR[self._term_chars],
                                                                 self._baud_rate))

                # To connect a serial instrument, baud_rate and read_termination is required
                self._instrument = self._rm.open_resource(resource_name=connection,
                                                          read_termination=read_term,
                                                          baud_rate=self._baud_rate)
            else:
                print('Connecting to VISA instrument: {} using: {}'.format(self.name, connection))
                self._instrument = self._rm.open_resource(connection)

        # TODO: allow for user defined instrument class
        else:
            raise NotImplementedError("At this time, the connection string must be provided")

    def _check_model(self):
        """Queries instrument for model ID and compares to models listed in driver
            Raises:
                ValueError --- if no model listed in driver appears in queried model
        """
        instrID = self.ask(self._driver['model_and_options']['model_cmd'])

        for model in self._driver['model_and_options']['models']:
            if model in instrID:
                return

        raise ValueError(f"No model listed in ['Models and options'] match the instruments model: '{instrID}'")

    def _initialize_visa_settings(self):
        """Initializes instrument settings using data in driver['VISA settings']"""
        if self._driver is not None:
            # timeout in ms
            self._timeout = float(self._driver['visa']['timeout']) * 1000
            self._term_chars = self._driver['visa']['term_char']
            self._send_end = self._driver['visa']['send_end_on_write']

            # used to determine if errors should be read after every read
            self._query_errors = self._driver['visa']['query_instr_errors']
        else:
            print('Driver dictionary is not defined!')

    def _get_serial_values(self):
        """Sets Instrument values for serial instruments"""
        self._baud_rate = self._driver['visa']['baud_rate']
        self._data_bits = self._driver['visa']['data_bits']
        self._stop_bits = self._driver['visa']['stop_bits']
        self._parity = str(self._driver['visa']['parity']).replace(' ', '_').lower()

    '''Set's default value for given quantity'''
    def _set_default_value(self, quantity):
        if self._driver['quantities'][quantity]['def_value']:
            self[quantity] = self._driver['quantities'][quantity]['def_value']

    def _startup(self):
        """Sends relevant start up commands to instrument"""
        self._instrument.write(self._driver['visa']['init'])

        _quantities = list(self._driver['quantities'].keys())

        # for quantity in _quantities:
        #     print(quantity)
        #     self.set_default_value(quantity)

    def close(self):
        """Sends final command to instrument if defined in driver and closes instrument and related resources"""
        # send final command
        if self._driver['visa']['final']:
            self.write(self._driver['visa']['final'])

        # close instrument
        self._instrument.close()
        # close resource manager
        self._rm.close()

    def ask(self, msg: str) -> str:
        """Queries instrument
        Parameters:
            msg -- message to be written to instrument
        Returns:
            string result from instrument
        """
        self._instrument.write(msg)
        return self._instrument.read()

    def write(self, msg):
        if msg:
            self._instrument.write(msg)

    def read(self):
        msg = self._instrument.read()
        if self._query_errors:
            msg += self._instrument.read()
        return msg

    def read_values(self, format):
        return self._instrument.read_values(format)

    def ask_for_values(self, msg, format):
        self.write(msg)
        return self.read_values(format)

    def clear(self):
        self._instrument.clear()

    def trigger(self, ):
        self._instrument.trigger()

    def read_raw(self):
        self._instrument.read_raw()

    @property
    def name(self):
        return self._driver['general_settings']['name']

    @property
    def quantity_values(self) -> dict:
        """Gets dictionary of all quantities with their values, settings, and options"""
        quants = dict(self._driver['quantities'])

        for quantity in quants.keys():
            quants[quantity]['value'] = self.get_value(quantity)

        return quants
    
    @property
    def quantities(self) -> dict:
        """Gets dictionary of all quantities without their values"""
        return dict(self._driver['quantities'])

    @property
    def quantity_names(self) -> list[str]:
        """Gets list of all quantity names"""
        return list(self._driver['quantities'].keys())

    @property
    def timeout(self) -> float:
        """Instrument timeout in seconds"""
        return self._instrument.timeout / 1000.00

    @timeout.setter
    def timeout(self, value):
        """Sets instrument timeout to value in seconds"""
        self._instrument.timeout = value * 1000

    @property
    def delay(self):
        """Instrument delay in seconds"""
        return self._instrument.delay

    @delay.setter
    def delay(self, value):
        """Sets instrument delay to value
        Parameters:
            value -- seconds
        """
        self._instrument.delay = value

    def get_value(self, quantity):
        """Gets value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        return self.ask(self._driver['quantities'][quantity]['get_cmd'])

    def set_default_value(self, quantity):
        """Sets default value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        print("Trying to set value")
        if self._driver['quantities'][quantity]['def_value']:
            self.set_value(quantity, self._driver['quantities'][quantity]['def_value'])

    def set_value(self, quantity, value):
        """Sets quantity to given value after performing checks on value
        Parameters:
            quantity -- Quantity name as provided in instrument driver
            value -- value to set quantity
        Raises:
            ValueError -- If value is outside of quantity's limits or predefined string values
        """
        self._check_limits(quantity, value)

        value = self._convert_value(quantity, value)

        # add the value to the command and write to instrument
        cmd = self._driver['quantities'][quantity]['set_cmd']
        if "<*>" in cmd:
            cmd = cmd.replace("<*>", str(value))
        else:
            cmd += f' {value}'

        self._instrument.write(cmd)

    def _check_limits(self, quantity, value):
        """Checks value against the limits or state values (for a combo) of a quantity
            Parameters:
                quantity -- qunatity whose limit to compare
                value -- value to compare against
            Raises:
                ValueError if value is out of range of limit or not in one of the combos states
        """
        lower_lim = self._driver['quantities'][quantity]['low_lim']
        upper_lim = self._driver['quantities'][quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")
        
        # check for valid states for Combos
        if self._driver['quantities'][quantity]['data_type'].upper() == 'COMBO':
            if self._driver['quantities'][quantity]['combo_cmd']:
                valid_states = list(self._driver['quantities'][quantity]['combo_cmd'].keys())
                valid_cmds = list(self._driver['quantities'][quantity]['combo_cmd'].values())
            else:
                raise ValueError(f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.")

            if value not in (valid_states or valid_cmds):
                raise ValueError(f"{value} is not a recognized state of {quantity}'s states. Valid states are {valid_states}.")
            
    def _convert_value(self, quantity, value):
        """Converts given value to pre-defined value in driver or returns the given value is N/A to convert
            Parameters:
                quantity -- quantity that holds the pre-defined value
                value -- value that needs converting
            Returns: 
                Converted value
            Raises:
                ValueError if quantity is a boolean but a boolean value is not provided
        """
        quantity_dict = self._driver['quantities'][quantity]

        # change boolean values to driver specified boolean values
        # Checks allow for user to pass in TRUE, FALSE, or driver-defined values
        if quantity_dict['data_type'].upper() == 'BOOLEAN':
            if value.upper() == ("TRUE" or self._driver['visa']['str_true'].upper()):
                return self._driver['visa']['str_true']
            elif value.upper() == ("FALSE" or self._driver['visa']['str_false'].upper()):
                return self._driver['visa']['str_false']
            else:
                raise ValueError(f"{value} is not a valid boolean value.")
            
        elif quantity_dict['data_type'].upper() == 'COMBO':
            # combo quantity contains no states or commands
            if not quantity_dict['combo_cmd']:
                raise ValueError(f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.")\
                
            # if user provided name of the state, convert, else return given value as it is already a valid value for the commandcommand
            if value in quantity_dict['combo_cmd'].keys():
                return quantity_dict['combo_cmd'][value]
        
        else:
            return value

    def _is_serial_instrument(self):
        return 'ASRL' in self._driver["instrument_interface"]["interface"]


    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
