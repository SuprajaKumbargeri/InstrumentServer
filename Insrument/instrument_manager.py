from pyvisa import *
import requests


class InstrumentManager:
    def __init__(self, name, connection):
        self._name = name

        self._get_driver()
        self._rm, self._instrument = self._initialize_resource_manager(connection)
        
        self._initialize_visa_settings()
        self._startup()

    '''Communicates with instrument server to get driver for instrument'''
    def _get_driver(self):
        # implementation will likely change
        url = r'http://localhost:5000/instrumentDB/getInstrument'
        response = requests.get(url, params={'cute_name': self._name})

        if 300 > response.status_code >= 200:
            self._driver = dict(response.json())
        else:
            response.raise_for_status()

    '''Initializes PyVISA resource if a PyVISA resource string was given at construction'''
    def _initialize_resource_manager(self, instrument_resource):
        # string passed through in VISA form
        if isinstance(instrument_resource, str):
            resource_manager = ResourceManager()
            instrument = resource_manager.open_resource(instrument_resource)

        # below will likely change
        else:
            resource_manager = None
            instrument = instrument_resource

        return resource_manager, instrument

    '''Initializes PyVISA instrument using data in VISA Settings'''
    def _initialize_visa_settings(self):
        # timeout in ms
        self._instrument.timeout = self._driver['visa']['timeout'] * 1000
        self._instrument.term_char = self._driver['visa']['term_char']
        self._instrument.send_end = self._driver['visa']['send_end_on_write']

        # used to determine if errors should be read after every read
        self._query_errors = self._driver['visa']['query_instr_errors']

    '''Sets Instrument values for serial instruments'''
    def _set_serial_values(self):
        self._instrument.baud_rate = self._driver['visa']['baud_rate']
        self._instrument.data_bits = self._driver['visa']['data_bits']
        self._instrument.stop_bits = self._driver['visa']['stop_bits']
        self._instrument.parity = self._driver['visa']['parity'].replace(' ', '_').lower()

    '''Set's default value for given quantity'''
    def _set_default_value(self, quantity):
        if self.quantities[quantity]['def_value']:
            self[quantity] = self.quantities[quantity]['def_value']

    def _startup(self):
        # Check models supported by driver
        if self._driver['model_and_options']['check_model']:
            model = self.model
            # TODO: Check if model matches given one in driver

        for quantity in self.quantities.keys():
            self._set_default_value(quantity)

        self._instrument.write(self._driver['visa']['init'])

    '''Closes instrument and PyVISA resource. Should be called when done using InstrumentManager'''
    def close(self):
        # send final command
        if self._driver['visa']['final']:
            self.write(self._driver['visa']['final'])

        # close instrument
        self._instrument.close()
        # close resource manager
        self._rm.close()

    def ask(self, msg):
        self._instrument.write(msg)
        return self._instrument.read()

    def write(self, msg):
        if msg:
            self._instrument.write(msg)

    def read(self):
        if self._query_errors:
            return self._instrument.read()
        return self._instrument.read()

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
        return self._name

    @property
    def model(self):
        return self.ask(self._driver['model_and_options']['model_cmd'])

    @property
    def options(self):
        return self.ask(self._driver['model_and_options']['option_cmd'])

    @property
    def quantities(self):
        return self._driver['quantities']

    @property
    def timeout(self):
        return self._instrument.timeout

    @property
    def delay(self):
        return self._instrument.delay

    def get_value(self, quantity):
        return self.ask(self.quantities[quantity]['get_cmd'])

    def set_value(self, quantity, value):
        lower_lim = self.quantities[quantity]['low_lim']
        upper_lim = self.quantities[quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        # change boolean values to driver specified boolean values
        if self.quantities[quantity]['data_type'].upper() == 'BOOLEAN':
            if value.upper() == "TRUE":
                value = self._driver['visa']['str_true']
            elif value.upper() == "FALSE":
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
