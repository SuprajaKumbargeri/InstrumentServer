import logging
import pyvisa


###################################################################################
# InstrumentDetectionService
###################################################################################
class InstrumentDetectionService:

    def __init__(self, logger: logging.Logger):
        self._my_logger = logger
        self._my_logger.debug(f'{self.__class__.__name__} initialized...')

    def detect_and_log_instruments(self):
        self.detect_and_log_visa_instruments()

    def detect_and_log_visa_instruments(self):
        self._my_logger.info(f'Detected the following VISA resources: \n{self.detect_visa_resources()}')

    def detect_visa_resources(self):
        """
        Detects all VISA resources attached to the system.
        """
        try:
            rm = pyvisa.ResourceManager()
            return rm.list_resources()
        except Exception as ex:
            return f'There was a problem detecting VISA resources: {ex}'

    def detect_serial_visa_instrument(self, resource_name: str, baud_rate: int, read_termination: str):
        """
        Detects specified serial VISA instrument attached to the system using pyVISA backend.
        """
        rm = pyvisa.ResourceManager()
        self._my_logger.info('Using baud_rate ' + str(baud_rate) + ' to connect to ' + resource_name)

        try:
            resource = rm.open_resource(resource_name=resource_name, read_termination=read_termination,
                                        baud_rate=baud_rate)
        except Exception as ex:
            self._my_logger.error(f'There was a problem connecting to serial VISA Instrument: \n{ex}')

        idn_str = str(resource.query('*IDN?'))
        self._my_logger.info(idn_str)


def main():
    """
    Run only for test purposes...
    """
    my_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    my_logger.setLevel(logging.INFO)

    service = InstrumentDetectionService(my_logger)
    service.detect_visa_resources()


if __name__ == "__main__":
    main()
