import logging
import pyvisa
from picoscope import *

###################################################################################
# InstrumentDetectionService
###################################################################################

class InstrumentDetectionService:

    def __init__(self, logger: logging.Logger):
        self.my_logger = logger

        # Key = Resource name
        # Value = pyVISA Resource 
        self.visa_instrument_resources = {}

        # Key = Resouce name
        # Value = Constructed "pico" instrument object PS6000
        self.pico_instruments = {}

        # Array with all serial VISA instrument names
        self.serial_instrument_names = []

    def detectInstruments(self):
        self.my_logger.debug("Detecting all instruments...")
        self.detect_visa_instruments()
        self.detect_pico_instruments()

        # TODO: Get params from DB...
        self.detect_serial_visa_instrument(self.serial_instrument_names[0], 115200, '\n')

        self.my_logger.info("Detected the following VISA Interfaces: " + str(self.visa_instrument_resources.keys()))
        self.my_logger.info("Detected the following pico Interfaces: " + str(self.pico_instruments.keys()))

    def detect_visa_instruments(self):
        """
        Detects all VISA compatible instruments attached to the system using the pyVISA 
        backend.
        """
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        self.my_logger.info('Detecting connected VISA Instruments...')

        # For all detected VISA resources...
        for inst in resources:
            resource = rm.open_resource(inst)

            # Query IDN for all non-serial instruments
            if ("ASRL" not in resource.resource_name):
                idn_str = str(resource.query('*IDN?'))

                # Remove the terminating \n
                idn_str = idn_str[:len(idn_str) - 1]
                model_name = idn_str.split(',')[1]

                # Key = MODEL_INTERFACE ex) 33220A_GPIB0
                key = model_name + '_' + str(resource.resource_name).split('::')[0]
                self.visa_instrument_resources[key] = resource
            else:
                self.my_logger.info("Detected Serial Interface VISA device: " + str(resource.resource_name))
                self.serial_instrument_names.append(resource.resource_name)

    def detect_pico_instruments(self):
        """
        Uses proprietary Python pip package that uses installed system DLLs (provided by Picoscope libraries) for
        actual communication with the instrument. Prerequisite is that these drivers are already
        installed on the system

        https://pypi.org/project/picoscope/
        """
        self.my_logger.info('Detecting connected Pico Instruments...')

        try:
            ps = ps6000.PS6000()
            self.pico_instruments[ps.LIBNAME.upper()] = ps
        except OSError: 
            self.my_logger.error("There was a problem loading DLLs for PS6000")

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
        idn_str = idn_str[:len(idn_str) - 1]
        model_name = idn_str.split(',')[1]

        key = model_name + '_' + 'SERIAL'
        self.visa_instrument_resources[key] = resource

    def get_visa_instruments(self):
        return  self.visa_instrument_resources

    def get_pico_instruments(self):
        return self.pico_instruments
         
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
