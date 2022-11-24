class InstrumentResource:

    def __init__(self, mfc: str, model: str, type: str, interface: str, driver: object):
        self.mfc = mfc
        self.model = model
        self.type = type
        self.interface = interface
        self.driver = driver

    def generate_summary(self) -> str:
        summary = 'Manufacturer: {0} \n'.format(self.mfc)
        summary += 'Model: {0} \n'.format(self.model)
        summary += 'Type: {0} \n'.format(self.type)
        summary += 'Interface: {0} \n'.format(self.interface)
        return summary

    def get_mfc(self):
        return self.mfc

    def get_model(self):
        return self.model

    def __str__(self):
        return 'InstrumentResource({0}, {1})'.format(self.model, self.interface)

