from enum import Enum
from pyvisa import ResourceManager
import requests
from copy import deepcopy

# Maps terminating character from ini file to actual character
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
    def __init__(self, name, connection, logger):
        self._name = name
        self._logger = logger
        self._instrument = None
        self.driver = None
        self._timeout = 1000.0
        self._term_chars = None
        self._send_end = None
        self._baud_rate = None
        self._data_bits = None
        self._stop_bits = None
        self._parity = None
        self._query_errors = None

        # Get the driver dictionary
        self._get_driver()
        self._get_visa_settings()

        if self._is_serial_instrument():
            self._get_serial_values()

        self._initialize_instrument(connection)

        # Set these after we have a PyVISA resource (self._instrument)
        self._initialize_visa_settings()

        if "ASLR" in self.driver["instrument_interface"]["interface"]:
            self._set_serial_values()

            # checks if model is correct, throws error if not
        self._check_model()
        self._startup()

    def _get_driver(self):
        """Communicates with instrument server to get driver for instrument"""
        # implementation will likely change
        url = r'http://127.0.0.1:5000/instrumentDB/getInstrument'
        response = requests.get(url, params={'cute_name': self._name})

        if 300 > response.status_code >= 200:
            self.driver = dict(response.json())
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

                self._logger.debug('Using the following parameters to connect to serial VISA instrument: resource_name={}, '
                      'read_termination={}, baud_rate={}'.format(connection,
                                                                 TERM_CHAR[self._term_chars],
                                                                 self._baud_rate))

                # To connect a serial instrument, baud_rate and read_termination is required
                self._instrument = self._rm.open_resource(resource_name=connection,
                                                          read_termination=read_term,
                                                          baud_rate=self._baud_rate,
                                                          open_timeout=10000)
            else:
                self._logger.debug('Connecting to VISA instrument: {} using: {}'.format(self.name, connection))
                self._instrument = self._rm.open_resource(connection)

        # TODO: allow for user defined instrument class
        else:
            raise NotImplementedError("At this time, the connection string must be provided")

    def _check_model(self):
        """Queries instrument for model ID and compares to models listed in driver
            Raises:
                ValueError --- if no model listed in driver appears in queried model
        """
        instrID = self.ask(self.driver['model_and_options']['model_cmd'])

        for model in self.driver['model_and_options']['models']:
            if model in instrID:
                return

        raise ValueError(f"No model listed in ['Models and options'] match the instruments model: '{instrID}'")

    def _get_visa_settings(self):
        self._logger.debug('Getting visa settings...')
        """Gets instrument settings using data in driver['VISA settings']"""
        if self.driver is not None:
            # timeout in ms
            self._timeout = float(self.driver['visa']['timeout']) * 1000
            self._term_chars = self.driver['visa']['term_char']
            self._send_end = self.driver['visa']['send_end_on_write']

            # used to determine if errors should be read after every read
            self._query_errors = self.driver['visa']['query_instr_errors']
        else:
            self._logger.warning('Driver dictionary is not defined!')

    def _get_serial_values(self):
        """Gets Instrument values for serial instruments"""
        self._baud_rate = self.driver['visa']['baud_rate']
        self._data_bits = self.driver['visa']['data_bits']
        self._stop_bits = self.driver['visa']['stop_bits']
        self._parity = str(self.driver['visa']['parity']).replace(' ', '_').lower()

    def _initialize_visa_settings(self):
        """Initializes instrument settings using data in driver['VISA settings']"""
        
        self._instrument.timeout = self._timeout
        self._instrument.term_chars = self._term_chars
        self._instrument.send_end = self._send_end

    def _set_serial_values(self):
        """Sets Instrument values for serial instruments"""
        self._instrument.baud_rate = self.driver['visa']['baud_rate']
        self._instrument.data_bits = self.driver['visa']['data_bits']
        self._instrument.stop_bits = self.driver['visa']['stop_bits']
        self._instrument.parity = self.driver['visa']['parity'].replace(' ', '_').lower()

    def _startup(self):
        """Sends relevant start up commands to instrument"""
        if self.driver['visa']['init']:
            self._instrument.write(self.driver['visa']['init'])

        if self.driver['quantities']:
            _quantities = list(self.driver['quantities'].keys())
        else:
            return

    def close(self):
        """Sends final command to instrument if defined in driver and closes instrument and related resources"""
        # send final command
        if self.driver['visa']['final']:
            self.write(self.driver['visa']['final'])

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
            self._logger.debug(f"Writing '{msg}' to '{self.name}.'")
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

    def get_quantity_info(self, quantity):
        """Returns only the necessary info for a given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        Returns:
            Dictionary containing info on quantity without any commands associated with it
        """
        quantity_info = deepcopy(self.driver['quantities'][quantity])
        del quantity_info['set_cmd']
        del quantity_info['get_cmd']
        del quantity_info['combo_cmd']

        if self.driver['quantities'][quantity]['data_type'].upper() == "COMBO":
            quantity_info['combos'] = self.driver['quantities'][quantity]['combo_cmd'].keys()
        else:
            quantity_info['combos'] = list()

        quantity_info['name'] = quantity
        quantity_info['latest_value'] = self.get_latest_value(quantity)
        return quantity_info

    def get_value(self, quantity):
        """Gets value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        value = self.ask(self.driver['quantities'][quantity]['get_cmd'])
        self._logger.info(f"'{quantity}' is set to '{value}.'")

        # Update latest value in DB in case it is incorrect
        self._set_latest_value(quantity, value)

        return self.convert_return_value(quantity, value)

    def get_latest_value(self, quantity):
        url = r'http://127.0.0.1:5000/instrumentDB/getLatestValue'
        response = requests.get(url, params={'cute_name': self._name, 'label': quantity})

        if 300 > response.status_code >= 200:
            return dict(response.json())['latest_value']
        else:
            response.raise_for_status()

    def set_default_value(self, quantity):
        """Sets default value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        if self.driver['quantities'][quantity]['def_value']:
            self.set_value(quantity, self.driver['quantities'][quantity]['def_value'])

    def set_value(self, quantity, value):
        """Sets quantity to given value after performing checks on value
        Parameters:
            quantity -- Quantity name as provided in instrument driver
            value -- value to set quantity
        Raises:
            ValueError -- If value is outside of quantity's limits or predefined string values
        """
        self._check_limits(quantity, value)

        value = self.convert_value(quantity, value)

        # add the value to the command and write to instrument
        cmd = self.driver['quantities'][quantity]['set_cmd']
        if "<*>" in cmd:
            cmd = cmd.replace("<*>", str(value))
        else:
            cmd += f' {value}'

        self._logger.debug(f"'{quantity}' is set to '{value}.'")
        self._instrument.write(cmd)
        self._set_latest_value(quantity, value)

    def _set_latest_value(self, quantity, value):
        url = r'http://127.0.0.1:5000/instrumentDB/setLatestValue'
        response = requests.put(url, params={'cute_name': self._name, 'label': quantity, 'latest_value': value})
        if response.status_code >= 300:
            response.raise_for_status()

    def _check_limits(self, quantity, value):
        """Checks value against the limits or state values (for a combo) of a quantity
            Parameters:
                quantity -- qunatity whose limit to compare
                value -- value to compare against
            Raises:
                ValueError if value is out of range of limit or not in one of the combos states
        """
        lower_lim = self.driver['quantities'][quantity]['low_lim']
        upper_lim = self.driver['quantities'][quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        # check for valid states for Combos
        if self.driver['quantities'][quantity]['data_type'].upper() == 'COMBO':
            if self.driver['quantities'][quantity]['combo_cmd']:
                valid_states = list(self.driver['quantities'][quantity]['combo_cmd'].keys())
                valid_cmds = list(self.driver['quantities'][quantity]['combo_cmd'].values())
            else:
                raise ValueError(f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.")

            if value not in (valid_states or valid_cmds):
                raise ValueError(f"{value} is not a recognized state of {quantity}'s states. Valid states are {valid_states}.")

    def convert_value(self, quantity, value):
        """Converts given value from user form to command form
            Parameters:
                quantity -- quantity that holds the pre-defined value
                value -- value that needs converting
            Returns:
                Converted value
            Raises:
                ValueError
        """
        quantity_dict = self.driver['quantities'][quantity]

        # change boolean values to driver specified boolean values
        # Checks allow for user to pass in TRUE, FALSE, or driver-defined values
        if quantity_dict['data_type'].upper() == 'BOOLEAN':
            value = str(value).strip()
            
            if value.upper() in ("TRUE", self.driver['visa']['str_true'].upper().strip()):
                return self.driver['visa']['str_true']
            elif value.upper() in ("FALSE", self.driver['visa']['str_false'].upper().strip()):
                return self.driver['visa']['str_false']
            else:
                raise ValueError(f"{value} is not a valid boolean value.")

        # Check Combo values
        elif quantity_dict['data_type'].upper() == 'COMBO':
            value = value.strip()

            # combo quantity contains no states or commands
            if not quantity_dict['combo_cmd']:
                raise ValueError(f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.") 
 
            # if user provided name of the state, convert it to command value 
            if value in (combo.strip() for combo in quantity_dict['combo_cmd'].keys()):
                return quantity_dict['combo_cmd'][value]
            # return given value as it is already a valid value for the command
            elif value in (combo.strip() for combo in quantity_dict['combo_cmd'].values()):
                return value
            # incorrect value given, raise error
            else:
                raise ValueError(f"Quantity '{quantity}' of type 'COMBO' has no ") 

        else:
            return value

    def convert_return_value(self, quantity, value):
        """Converts given value from command form to user form
            Parameters:
                quantity -- quantity that holds the pre-defined value
                value -- value that needs converting
            Returns:
                Converted value
            Raises:
                ValueError
        """
        quantity_dict = self.driver['quantities'][quantity]

        # change driver specified boolean values to boolean value
        if quantity_dict['data_type'].upper() == 'BOOLEAN':
            value = str(value).strip()
            if value.upper() == self.driver['visa']['str_true'].upper().strip():
                return True
            elif value.upper() == self.driver['visa']['str_false'].upper().strip():
                return False
            else:
                raise ValueError(f"{self.name} returned an invalid value for {quantity}. {value} is not a valid boolean value. Please check instrument driver.")
            
        # Instrument will return instrument-defined value, convert it to driver-defined value
        elif quantity_dict['data_type'].upper() == 'COMBO':
            value = value.strip()

            # key contains driver-defined value, cmd contains instrument-defined value
            # need to return driver-defined value
            for key, cmd in quantity_dict['combo_cmd'].items():
                if value in (key.strip(), cmd.strip()):
                    return key

            raise ValueError(f"{self.name} returned an invalid value for {quantity}. {value} is not a valid combo value. Please check instrument driver.")
        
        else:
            return value

    def _is_serial_instrument(self):
        """Does current instrument use serial to communicate?"""
        interface = self.driver["instrument_interface"]["interface"]
        return 'ASRL' in interface or 'COM' in interface

    # Properties and setters
    @property
    def name(self):
        return self._name

    # region VISA Settings
    @property
    def use_visa(self) -> bool:
        return self.driver['visa']['use_visa']

    @use_visa.setter
    def use_visa(self, value: bool):
        self.driver['visa']['use_visa'] = value

    @property
    def reset(self) -> bool:
        return self.driver['visa']['reset']

    @reset.setter
    def reset(self, value: bool):
        self.driver['visa']['reset'] = value

    @property
    def query_instr_errors(self) -> bool:
        return self.driver['visa']['query_instr_errors']

    @query_instr_errors.setter
    def query_instr_errors(self, value: bool):
        self.driver['visa']['query_instr_errors'] = value

    @property
    def error_bit_mask(self) -> int:
        return self.driver['visa']['error_bit_mask']

    @error_bit_mask.setter
    def error_bit_mask(self, value: int):
        self.driver['visa']['error_bit_mask'] = value

    @property
    def error_cmd(self) -> str:
        return self.driver['visa']['error_cmd']

    @error_cmd.setter
    def error_cmd(self, value: str):
        self.driver['visa']['error_cmd'] = value

    @property
    def init_cmd(self) -> str:
        return self.driver['visa']['init']

    @init_cmd.setter
    def init_cmd(self, value: str):
        self.driver['visa']['init'] = value

    @property
    def final_cmd(self) -> str:
        return self.driver['visa']['final']

    @final_cmd.setter
    def final_cmd(self, value: str):
        self.driver['visa']['final'] = value

    @property
    def str_true(self) -> str:
        return self.driver['visa']['str_true']

    @str_true.setter
    def str_true(self, value: str):
        self.driver['visa']['str_true'] = value

    @property
    def str_false(self) -> str:
        return self.driver['visa']['str_false']

    @str_false.setter
    def str_false(self, value: str):
        self.driver['visa']['str_false'] = value

    @property
    def str_value_out(self) -> str:
        return self.driver['visa']['str_value_out']

    @str_value_out.setter
    def str_value_out(self, value: str):
        self.driver['visa']['str_value_out'] = value

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
    # endregion

    @property
    def quantities(self) -> dict:
        """Gets dictionary of all quantities without their values"""
        return dict(self.driver['quantities'])

    @property
    def quantity_names(self) -> list[str]:
        """Gets list of all quantity names"""
        return list(self.driver['quantities'].keys())

    @property
    def quantity_values(self) -> dict:
        """Gets dictionary of all quantities with their values, settings, and options"""
        quants = dict(self.driver['quantities'])

        for quantity in quants.keys():
            quants[quantity]['value'] = self.get_value(quantity)

        return quants

    # Built-in methods
    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
