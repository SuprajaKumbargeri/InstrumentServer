from enum import Enum
from pyvisa import ResourceManager
import requests
from typing import Callable

from .quantity_manager import QuantityManager

# Maps terminating character from ini file to actual character
TERM_CHAR = Enum('TERM_CHAR',
                 {'Auto': 'Auto',
                  'None': '',
                  'CR': '\r',
                  'LF': '\n',
                  'CR+LF': '\r\n'})


###################################################################################
# InstrumentManager
###################################################################################
class InstrumentManager:
    def __init__(self, name, connection, driver, logger):
        self._name = name
        self._logger = logger
        self._rm = None
        self._instrument = None
        self._driver = driver
        self._timeout = 1000.0
        self._term_chars = None
        self._send_end = None
        self._baud_rate = None
        self._data_bits = None
        self._stop_bits = None
        self._parity = None
        self.query_errors = None
        self.quantities = dict()

        try:
            # Set VISA driver parameters
            self._initialize_visa_settings()

            if self._is_serial_instrument():
                # Set SERIAL parameters
                self._initialize_serial_settings()

            # Try to connect to the instrument (all exceptions caught below)
            self._initialize_instrument(connection)

            self._check_model()
            self._initialize_quantities()
            self._startup()
        except Exception as ex:
            # Close the instrument if we happen to be connected to it already
            self.close()

            raise Exception(f'There was a problem constructing a Instrument Manager for instrument: {ex}')

    def _initialize_instrument(self, connection):
        """Initializes PyVISA resource if a PyVISA resource string was given at construction"""
        # string passed through in VISA form
        if isinstance(connection, str):
            self._rm = ResourceManager()

            if self._is_serial_instrument():
                self._connect_to_serial_instrument(connection)
            else:
                self._logger.info(f'Connecting to VISA instrument: {self.name} using: {connection}')
                self._instrument = self._rm.open_resource(connection)

            # After we have the connected VISA resource, set visa and serial settings
            self._set_visa_settings_in_visa_resource()

            if self._is_serial_instrument():
                self._set_serial_settings_in_visa_resource()

        # TODO: allow for user defined instrument class
        else:
            raise NotImplementedError("At this time, the connection string must be provided")

    def _connect_to_serial_instrument(self, connection_str):
        # To connect a serial instrument, baud_rate and read_termination is required, check if these
        # are defined for the instrument

        if self._term_chars is None:
            raise Exception('No termination character(s) defined for serial instrument')

        if self._baud_rate is None:
            raise Exception('No baud rate defined for serial instrument')

        # Converts termination character into actual value
        read_term = str(TERM_CHAR[self._term_chars].value)

        self._logger.info(f'Connecting to SERIAL VISA instrument: where resource_name={connection_str},'
                          f' read_termination={self._term_chars}, baud_rate={self._baud_rate}')

        self._instrument = self._rm.open_resource(resource_name=connection_str,
                                                  read_termination=read_term,
                                                  baud_rate=self._baud_rate,
                                                  open_timeout=10000)

    def _check_model(self):
        """Queries instrument for model ID and compares to models listed in driver
            Raises:
                ValueError --- if no model listed in driver appears in queried model
        """
        instrID = self.ask(self._driver['model_and_options']['model_cmd'])

        for model in self._driver['model_and_options']['models']:
            if model in instrID:
                return

        raise ValueError(f"No model listed in ['Models and options'] match the instruments model: '{instrID}'")

    def _initialize_visa_settings(self):
        """Initializes instrument settings using data in driver['VISA']"""
        self._timeout = float(self._driver['visa']['timeout']) * 1000  # 1000 ms in 1s
        self._term_chars = self._driver['visa']['term_char']
        self._send_end = self._driver['visa']['send_end_on_write']
        self._query_errors = self._driver['visa']['query_instr_errors']

    def _set_visa_settings_in_visa_resource(self):
        self._instrument.timeout = self._timeout
        self._instrument.term_chars = self._term_chars
        self._instrument.send_end = self._send_end
        self.query_errors = self._query_errors

    def _initialize_serial_settings(self):
        """Sets Instrument values for serial instruments"""
        self._baud_rate = self._driver['visa']['baud_rate']
        self._data_bits = self._driver['visa']['data_bits']
        self._stop_bits = self._driver['visa']['stop_bits']

        if self._driver['visa']['parity']:
            self._parity = str(self._driver['visa']['parity']).replace(' ', '_').lower()

    def _set_serial_settings_in_visa_resource(self):
        self._instrument.baud_rate = self._baud_rate

        if self._data_bits:
            self._instrument.data_bits = self._data_bits

        if self._stop_bits:
            # TODO: Implement to use Enum like (StopBits.one)
            pass

        if self._parity:
            self._instrument.parity = self._parity

    def _initialize_quantities(self):
        str_true = self._driver['visa']['str_true']
        str_false = self._driver['visa']['str_false']

        for name, info in self._driver['quantities'].items():
            self.quantities[name] = QuantityManager(info, self.write, self.read, str_true, str_false, self._logger)

    def _startup(self):
        """Sends relevant start up commands to instrument"""
        if self._driver['visa']['init']:
            self._instrument.write(self._driver['visa']['init'])

    def close(self):
        """Sends final command to instrument if defined in driver and closes instrument and related resources"""
        # send final command
        if self._driver['visa']['final']:
            self.write(self._driver['visa']['final'])

        # close instrument
        if self._instrument:
            self._instrument.close()
        # close resource manager
        if self._rm:
            self._rm.close()

    def ask(self, msg: str) -> str:
        """Queries instrument
        Parameters:
            msg -- message to be written to instrument
        Returns:
            string result from instrument
        """
        self._instrument.write(msg)
        return self._instrument.read()

    def write(self, msg):
        if msg:
            self._logger.debug(f"Writing '{msg}' to '{self.name}.'")
            self._instrument.write(msg)

    def read(self):
        return self._instrument.read()

    def read_values(self, format):
        return self._instrument.read_values(format)

    def ask_for_values(self, msg, format):
        self.write(msg)
        return self._instrument.read_values(format)

    def clear(self):
        self._instrument.clear()

    def trigger(self, ):
        self._instrument.trigger()

    def read_raw(self):
        self._instrument.read_raw()

    @property
    def name(self):
        return self._name

    @property
    def model_name(self):
        return self._driver['instrument_interface']['manufacturer']

    @property
    def address(self):
        return self._driver['instrument_interface']['address']

    @property
    def timeout(self) -> float:
        """Instrument timeout in seconds"""
        return float(self._instrument.timeout) / 1000.0

    @timeout.setter
    def timeout(self, value):
        """Sets instrument timeout to value in seconds"""
        self._instrument.timeout = float(value) * 1000.0

    @property
    def delay(self):
        """Instrument delay in seconds"""
        return self._instrument.delay

    @delay.setter
    def delay(self, value):
        """Sets instrument delay to value
        Parameters:
            value -- seconds
        """
        self._instrument.delay = value

    def get_visible_quantities(self) -> list[QuantityManager]:
        """Returns a list of all visible quantities"""
        return [quantity for quantity in self.quantities.values() if quantity.is_visible]

    def link_quantity(self, quantity: str, link_to: QuantityManager, link_set: bool, link_get: bool):
        """"""
        if link_set:
            self.quantities[quantity].linked_quantity_set = link_to
        else:
            self.quantities[quantity].linked_quantity_set = None
        if link_get:
            self.quantities[quantity].linked_quantity_get = link_to
        else:
            self.quantities[quantity].linked_quantity_get = None

    def get_value(self, quantity):
        """Gets value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        value = self.quantities[quantity]
        self.update_visibility(quantity, value)
        return value

    def get_latest_value(self, quantity):
        return self.quantities[quantity].latest

    def set_default_value(self, quantity):
        """Sets default value for given quantity
        Parameters:
            quantity -- Quantity name as provided in instrument driver
        """
        if self._driver['quantities'][quantity]['def_value']:
            self.set_value(quantity, self._driver['quantities'][quantity]['def_value'])

    def set_value(self, quantity, value):
        """Sets quantity to given value after performing checks on value
        Parameters:
            quantity -- Quantity name as provided in instrument driver
            value -- value to set quantity
        Raises:
            ValueError -- If value is outside of quantity's limits or predefined string values
        """
        self.quantities[quantity].set_value(value)
        self.update_visibility(quantity, value)

    def update_visibility(self, quantity_changed, new_value):
        """Updates visibility of all quantities whose state_quant is the quantity_changed
            Parameters:
                quantity_changed -- qunatity whose value was just changed
                new_value -- value that quantity was just changed to
        """
        converted_value = self.quantities[quantity_changed].convert_return_value(new_value)

        for quantity in self.quantities.values():
            if quantity.state_quant != quantity_changed:
                continue

            # allows user to insert either the user form or command form of the state value in .ini
            if str(converted_value) in quantity.state_values or str(new_value) in quantity.state_values:
                quantity.is_visible = True
            else:
                quantity.is_visible = False

    def _is_serial_instrument(self):
        """Does current instrument use serial to communicate?"""
        is_serial = self._driver["instrument_interface"]["serial"]
        return bool(is_serial)

    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
