import logging
import pyvisa
from . instrument_resource import InstrumentResource, INST_TYPE

###################################################################################
# InstrumentDetectionService
###################################################################################


class InstrumentDetectionService:

    def __init__(self, logger: logging.Logger):
        self.my_logger = logger

    def detectInstruments(self):
        self.detect_visa_instruments()

    def detect_visa_instruments(self):
        """
        Detects all VISA compatible instruments attached to the system using pyVISA backend.
        """
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        self.my_logger.info('VISA resources: {}'.format(resources))


    def detect_serial_visa_instrument(self, resource_name: str, baud_rate: int,  read_termination: str):
        """
        Detects specified serial VISA instrument attached to the system using pyVISA backend.
        """
        rm = pyvisa.ResourceManager()
        self.my_logger.info('Using baud_rate ' + str(baud_rate) + ' to connect to ' + resource_name)

        try:
            resource = rm.open_resource(resource_name=resource_name,  read_termination=read_termination, baud_rate=baud_rate)
        except Exception:
            self.my_logger.error('There was a problem connecting to serial VISA Instrument')

        idn_str = str(resource.query('*IDN?'))

        # Example IDN response:
        # DS Instruments,SG22000PRO,411,V4.65
        self.visa_instrument_resources.append(self.construct_instrument_resource(resource, idn_str, INST_TYPE.VISA))


def main():
    my_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    my_logger.setLevel(logging.INFO)

    instService = InstrumentDetectionService(my_logger)
    instService.detectInstruments()

if __name__ == "__main__":
    main()
