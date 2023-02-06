class Instrument:
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
