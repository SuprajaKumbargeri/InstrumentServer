import logging
import pyvisa
from picoscope import *
from . instrument_resource import InstrumentResource, INST_TYPE

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
        self.detect_visa_instruments()

        '''
        self.detect_serial_visa_instrument(self.serial_instrument_names[0], 115200, '\n')
        self.detect_tcpip_visa_instrument('192.168.0.7', '\n', '\n')

        self.detect_pico_instruments()

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
        '''


    def detect_visa_instruments(self):
        """
        Detects all VISA compatible instruments attached to the system using pyVISA 
        backend.
        """
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        self.my_logger.info('VISA resources: {}'.format(resources))

        '''
        # For all detected VISA resources...
        for inst in resources:
            resource = rm.open_resource(inst)

            # Query IDN for all non-serial instruments
            if ("ASRL" not in resource.resource_name):
                idn_str = str(resource.query('*IDN?'))

                # Example IDN response:
                # Agilent Technologies,33220A,SG44001573,2.02-2.02-22-2
                self.visa_instrument_resources.append(self.construct_instrument_resource(resource, idn_str, INST_TYPE.VISA))

            else:
                self.my_logger.info("Detected Serial Interface VISA device: " + str(resource.resource_name))
                self.serial_instrument_names.append(resource.resource_name)
        '''


    def detect_pico_instruments(self):
        """
        Uses proprietary Python pip package that uses installed system DLLs (provided by Picoscope libraries) for
        actual communication with the instrument. Prerequisite is that these drivers are already
        installed on the system

        https://pypi.org/project/picoscope/
        """
        self.my_logger.info('Detecting connected Pico Technology Instruments...')

        try:
            #SERIAL_NUM = 'AR571/017\x00'
            ps = ps6000.PS6000(serialNumber=None, connect=False)

            #Open Pico Instrument Asynchronously
            ps.openUnitAsync(serialNumber=None)

            inst_resource = InstrumentResource('Pico Technology', 'PS6000', INST_TYPE.PICO, 'USB', ps)
            self.pico_instruments.append(inst_resource)
        except OSError as ex: 
            self.my_logger.error("There was a problem opening PS6000: " + str(ex))


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


    def detect_tcpip_visa_instrument(self, ip_addr: str, write_termination: str, read_termination: str):
        """
        Detects specified TCP/IP VISA instrument attached to the system using pyVISA backend.
        """
        # Default LAN Device Name is inst0
        LAN_DEVICE = 'inst0'
        INTERFACE = 'TCPIP0'

        rm = pyvisa.ResourceManager()
        address_string = INTERFACE + "::" + ip_addr + "::" + "INSTR"

        self.my_logger.info('Attempting to connect to VISA instrument over TCP/IP using address {}'.format(ip_addr))

        try:
            resource = rm.open_resource(address_string, read_termination=read_termination, write_termination=write_termination)
        except Exception:
            self.my_logger.error('There was a problem connecting to TCPIP VISA Instrument')

        idn_str = str(resource.query('*IDN?'))
        self.visa_instrument_resources.append(self.construct_instrument_resource(resource, idn_str, INST_TYPE.VISA, ip_addr))


    def get_visa_instruments(self):
        return  self.visa_instrument_resources


    def get_pico_instruments(self):
        return self.pico_instruments

    def construct_instrument_resource(self, resource, idn_str: str, inst_type: INST_TYPE, ip=None) -> InstrumentResource:
        # Remove the terminating \n
        idn_str = idn_str[:len(idn_str) - 1]

        # Split IDN output into list
        idn_lst = idn_str.split(',')

        # Construct Instrument Resource
        return InstrumentResource(idn_lst[0], idn_lst[1], INST_TYPE.VISA , str(resource.resource_name).split('::')[0], resource, ip)


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
