class Instrument:
    """Base class that should be implemented as a driver for any instrumrent that does not support VISA protocol"""

    def write(self, msg):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def read_values(self, format):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def trigger(self):
        raise NotImplementedError()

    def read_raw(self):
        raise NotImplementedError()

    @property
    def timeout(self):
        pass

    @set.timeout
    def timeout(self, value):
        pass

    @property
    def term_chars(self):
        pass

    @set.term_chars
    def term_chars(self, value):
        pass

    @property
    def values_format(self):
        pass

    @set.values_format
    def values_format(self, value):
        pass

    @property
    def baud_rate(self):
        pass

    @set.baud_rate
    def baud_rate(self, value):
        pass

    @property
    def data_bits(self):
        pass

    @set.data_bits
    def data_bits(self, value):
        pass

    @property
    def stop_bits(self):
        pass

    @set.stop_bits
    def stop_bits(self, value):
        pass

    @property
    def parity(self):
        pass

    @set.parity
    def parity(self, value):
        pass

    @property
    def end_input(self):
        pass

    @set.end_input
    def end_input(self, value):
        pass

