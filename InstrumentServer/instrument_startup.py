import logging
import pyvisa

def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger

def log_instruments():
    rm = pyvisa.ResourceManager()
    my_logger.debug(rm.list_resources())
