import logging
from pyvisa import *
from picoscope import *
from .. InstrumentDetection.instrument_resource import *

class InstrumentComService:

    def __init__(self, logger: logging.Logger, visa_inst_list: InstrumentResource , pico_int_list: InstrumentResource):
        self.logger = logger
        self.visa_instrument_resources = visa_inst_list
        self.pico_instruments = pico_int_list

    def close_all_instruments(self):
        logger.info("Closing all connections to known Instruments...")

        for inst in self.visa_instrument_resources:
            logger.info("Closing {}".format(inst.get_model()))
            driver = inst.get_driver()
            driver.close()

        for inst in self.pico_instruments:
            logger.info("Closing {}".format(inst.get_model()))
            driver = inst.get_driver()
            driver.close()

    def handle_ask(self, instrument: str, cmd: str, type: INST_TYPE):

        logger.info("handle_ask() - instrument: " + instrument + " cmd: " + cmd)

        if type == INST_TYPE.VISA:
            for instument_resource in self.visa_instrument_resources:
                if instument_resource.get_model() == instrument.upper():
                    driver = instument_resource.get_driver()

                    try:
                        self.logger.info(f"Querying: {cmd}")
                        response = driver.query(cmd)
                        self.logger.info(f"Response: {response}")
                        return response

                    except Exception as e:
                        inst = repr(self)
                        e.args = e.args + ("asking " + repr(cmd) + " to " + inst,)
                        return 500  

        elif type == INST_TYPE.PICO:
            logging.info("Pico not yet implemented!")

        return 404

        
