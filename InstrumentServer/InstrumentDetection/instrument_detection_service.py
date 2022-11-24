import logging
import pyvisa
from picoscope import *
from . instrument_resource import InstrumentResource

###################################################################################
# InstrumentDetectionService
###################################################################################


class InstrumentDetectionService:

    def __init__(self, logger: logging.Logger):
        self.my_logger = logger

        self.visa_instrument_resources = []
        self.pico_instruments = []

        # Array with all serial VISA instrument names
        self.serial_instrument_names = []

    def detectInstruments(self):
        self.my_logger.debug("Detecting all instruments...")
        self.detect_visa_instruments()
        self.detect_pico_instruments()

        # TODO: Get params from DB...
        self.detect_serial_visa_instrument(self.serial_instrument_names[0], 115200, '\n')

        visa_report = 'Detected the following VISA Interfaces: \n'
        for inst in self.visa_instrument_resources:
            visa_report += inst.generate_summary()
            visa_report += '\n'
        self.my_logger.info(visa_report)

        pico_report = "Detected the following PICO Interfaces: \n"
        for inst in self.pico_instruments:
            pico_report += inst.generate_summary()
            pico_report += '\n'
        self.my_logger.info(pico_report)


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

                # Example IDN response:
                # Agilent Technologies,33220A,SG44001573,2.02-2.02-22-2

                # Remove the terminating \n
                idn_str = idn_str[:len(idn_str) - 1]

                # Split IDN output into list
                idn_lst = idn_str.split(',')

                # Construct Instrument Resource
                inst_resource = InstrumentResource(idn_lst[0], idn_lst[1], 'VISA', str(resource.resource_name).split('::')[0], resource)
                self.visa_instrument_resources.append(inst_resource)

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
        self.my_logger.info('Detecting connected Pico Technology Instruments...')

        try:
            ps = ps6000.PS6000()
            inst_resource = InstrumentResource('Pico Technology', 'PS6000', 'PICO', 'USB', ps)
            self.pico_instruments.append(inst_resource)
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

        # Example IDN response:
        # DS Instruments,SG22000PRO,411,V4.65

        # Remove the terminating \n
        idn_str = idn_str[:len(idn_str) - 1]

        # Split IDN output into list
        idn_lst = idn_str.split(',')

        # Construct Instrument Resource
        inst_resource = InstrumentResource(idn_lst[0], idn_lst[1], 'SERIAL', str(resource.resource_name).split('::')[0], resource)
        self.visa_instrument_resources.append(inst_resource)


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
