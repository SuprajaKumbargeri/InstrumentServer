from enum import Enum

class INST_TYPE(Enum):
    VISA = 'VISA'
    PICO = 'PICO'

class InstrumentResource:

    def __init__(self, mfc: str, model: str, type: INST_TYPE, interface: str, driver: object):
        self.mfc = mfc
        self.model = model
        self.type = type
        self.interface = interface
        self.driver = driver

    def generate_summary(self) -> str:
        summary = 'Manufacturer: {0} \n'.format(self.mfc)
        summary += 'Model: {0} \n'.format(self.model)
        summary += 'Type: {0} \n'.format(self.type.value)
        summary += 'Interface: {0} \n'.format(self.interface)
        return summary

    def get_mfc(self) -> str:
        return self.mfc

    def get_model(self) -> str:
        return self.model

    def get_type(self) -> INST_TYPE:
        return self.type

    def get_driver(self) -> object:
        return self.driver

    def __str__(self):
        return 'InstrumentResource({0}, {1})'.format(self.model, self.interface)

