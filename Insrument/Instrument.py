from pyvisa import *


class BaseInstrument:
    def __int__(self, name):
        self._name = name

    def ask(self, msg):
        raise NotImplementedError()

    def write(self, msg):
        raise NotImplementedError()

    def read(self, msg):
        raise NotImplementedError()

    def read_values(self, msg):
        raise NotImplementedError()

    def ask_for_values(self, msg):
        raise NotImplementedError()

    def clear(self, msg):
        raise NotImplementedError()

    def trigger(self, msg):
        raise NotImplementedError()

    def read_raw(self, msg):
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
        pass

    def read(self, msg):
        pass

    def read_values(self, msg):
        pass

    def ask_for_values(self, msg):
        pass

    def clear(self, msg):
        pass

    def trigger(self, msg):
        pass

    def read_raw(self, msg):
        pass

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
        self._instr.timeout = value

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
