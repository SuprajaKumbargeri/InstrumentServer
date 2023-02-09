from pyvisa import *
import requests


class InstrumentManager:
    def __init__(self, name, connection):
        self._name = name

        self._get_driver()
        self._initialize_instrument(connection)
        self._check_model()

        self._initialize_visa_settings()
        self._startup()

    def _get_driver(self):
        """Communicates with instrument server to get driver for instrument"""
        # implementation will likely change
        url = r'http://localhost:5000/instrumentDB/getInstrument'
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
        # timeout in ms
        self._instrument.timeout = self._driver['visa']['timeout'] * 1000
        self._instrument.term_chars = self._driver['visa']['term_char']
        self._instrument.send_end = self._driver['visa']['send_end_on_write']

        # used to determine if errors should be read after every read
        self._query_errors = self._driver['visa']['query_instr_errors']

    def _set_serial_values(self):
        """Sets Instrument values for serial instruments"""
        self._instrument.baud_rate = self._driver['visa']['baud_rate']
        self._instrument.data_bits = self._driver['visa']['data_bits']
        self._instrument.stop_bits = self._driver['visa']['stop_bits']
        self._instrument.parity = self._driver['visa']['parity'].replace(' ', '_').lower()

    def _startup(self):
        """Sends relavent start up commands to instrument"""
        self._instrument.write(self._driver['visa']['init'])

        for quantity in self.quantities.keys():
            self.set_default_value(quantity)

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
    def quantities(self) -> dict:
        """Gets dictionary of all quantities, their values, settings, and options"""
        quantities = dict(self._driver['quantities'])

        for quantity in quantities.keys():
            quantities[quantity]['value'] = self.get_value(quantity)

        return quantities

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
    def delay(selfself, value):
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
        if self.quantities[quantity]['def_value']:
            self[quantity] = self.quantities[quantity]['def_value']

    def set_value(self, quantity, value):
        """Sets quantity to given value after performing checks on value
        Parameters:
            quantity -- Quantity name as provided in instrument driver
            value -- value to set quantity
        Raises:
            ValueError -- If value is outside of quantity's limits or predefined string values
        """
        lower_lim = self.quantities[quantity]['low_lim']
        upper_lim = self.quantities[quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        # change boolean values to driver specified boolean values
        if self.quantities[quantity]['data_type'].upper() == 'BOOLEAN':
            if str(value).upper() == "TRUE":
                value = self._driver['visa']['str_true']
            elif str(value).upper() == "FALSE":
                value = self._driver['visa']['str_false']

        # add the value to the command and write to instrument
        cmd = self.quantities[quantity]['set_cmd']
        if "<*>" in cmd:
            cmd = cmd.replace("<*>", str(value))
        else:
            cmd += f' {value}'

        self._instrument.write(cmd)

    def get_state(self, quantity):
        if self.quantities[quantity]['state_quant']:
            return self.quantities[quantity]['state_quant']
        return None

    def set_state(self, quantity, state):
        if state not in self.quantities[quantity]['state_values']:
            raise ValueError(f'{state} is not a valid state for {quantity}.')
        self.quantities[quantity]['state_quant'] = state

    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
