from pyvisa import *
from configparser import ConfigParser
import requests
from urllib.error import HTTPError

class BaseInstrument:
    def ask(self, msg):
        raise NotImplementedError()

    def write(self, msg):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def read_values(self, format):
        raise NotImplementedError()

    def ask_for_values(self, msg, format):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def trigger(self):
        raise NotImplementedError()

    def read_raw(self):
        raise NotImplementedError()

    @property
    def name(self):
        raise NotImplementedError()


class InstrumentManager(BaseInstrument):
    def __init__(self, driver, instrument_resource):
        self._initialize_driver(driver)
        self._driver = self.parse_driver(driver)
        self._rm, self._instrument = self._initialize_resource_manager(instrument_resource)

        self._name = self._driver['General settings']['name']
        self._initialize_visa_settings()
        self._startup()

    def _initialize_driver(self, driver):
        url = r'http://localhost:5000/driverParser/'
        response = requests.get(url, data={'driverPath': driver})

        if 300 > response.status_code >= 200:
            self._driver = dict(response.json())
        else:
            response.raise_for_status()

    def _initialize_resource_manager(self, instrument_resource):
        # string passed through in VISA form
        if isinstance(instrument_resource, str):
            resource_manager = ResourceManager()
            instrument = resource_manager.open_resource(instrument_resource)

        else:
            resource_manager = None
            instrument = instrument_resource

        return resource_manager, instrument

    '''Initializes PyVISA instrument using data in VISA Settings'''
    def _initialize_visa_settings(self):
        # timeout in ms
        self._instrument.timeout = self._driver['visa']['timeout'] * 1000
        # self._instrument.term_char = self._driver['visa']['term_char']

        # used to determine if errors should be read after every read
        self._query_errors = self._driver['visa']['query_instr_errors']
    
    def _startup(self):
        # Check models supported by driver
        if self._driver['model']['check_model']:
            model = self.model
            # if model not in list(self._driver['model']['models'].values()):
            #     raise ValueError(f"The current driver does not support the instrument {model}.")

        self._instrument.write(self._driver['visa']['init'])

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
        return self.ask(self._driver['model']['model_cmd'])

    @property
    def options(self):
        return self.ask(self._driver['model']['option_cmd'])

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

        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '-INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        cmd = self.quantities[quantity]['set_cmd']
        if "<*>" in cmd:
            cmd.replace("<*>", value)
        else:
            cmd += value

        self._instrument.write()

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
