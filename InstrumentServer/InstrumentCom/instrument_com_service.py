import logging
from pyvisa import *
from picoscope import *
from .. InstrumentDetection.instrument_resource import *

class InstrumentComService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def close_all_instruments(self):
        pass      
