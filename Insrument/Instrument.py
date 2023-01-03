from pyvisa import *


class BaseInstrument:
    def __int__(self, name):
        self._name = name

    def ask(self, msg):
        raise NotImplementedError()

    def write(self, msg):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def read_values(self):
        raise NotImplementedError()

    def ask_for_values(self, format):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def trigger(self):
        raise NotImplementedError()

    def read_raw(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self._name


class Instrument(BaseInstrument):
    def __int__(self, driver, instrument_resource, name=None):
        # parse driver
        self._config = {}
        self._rm, self._instrument = self._initialize_resource_manager(instrument_resource)

        if name is None:
            self._name = self.model
        else:
            super().__int__(name)

    def _initialize_resource_manager(self, instrument_resource):
        # string passed through in VISA form
        if isinstance(instrument_resource, str):
            resource_manager = ResourceManager()
            instrument = resource_manager.get_instrument(instrument_resource)
        else:
            resource_manager = None
            instrument = instrument_resource

        return resource_manager, instrument

    def close(self):
        self._rm.close()

    def ask(self, msg):
        return self._instrument.ask(msg)

    def write(self, msg):
        self._instrument.write(msg)

    def read(self):
        return self._instrument.read()

    def read_values(self, format):
        return self._instrument.read_values(format)

    def ask_for_values(self, msg):
        pass

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
        return self._instrument.ask(self._config['model']['option_cmd'])

    @property
    def options(self):
        return self._instrument.ask(self._config['model']['option_cmd'])

    @property
    def quantities(self):
        return self._config['Quantities']

    @property
    def timeout(self):
        return self._instrument.timeout

    @timeout.setter
    def timeout(self, value):
        self._instrument.timeout = value

    @property
    def delay(self):
        return self._instrument.delay

    @delay.setter
    def delay(self, value):
        self._instrument.delay = value

    def get_value(self, quantity):
        return self._instrument.ask(self.quantities[quantity]['get_cmd'])

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

    def __setitem__(self, item, value):


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
