from picoscope import *
import requests
import time
import matplotlib.pyplot as plt
import numpy as np

# import sys
# sys.path.append('/Picoscope_6000')
# from Picoscope_6000.Picoscope_6000 import Driver

class PicoscopeManager:
    def __init__(self, name, driver):
        self._name = name
        self._driver = driver
        self._ps = self._initialize_picoscope()

    '''Communicates with instrument server to get driver for instrument'''

    # def _initialize_driver(self, driver):
    #     # implementation will likely change
    #     url = r'http://localhost:5000/driverParser/'
    #     response = requests.get(url, data={'driverPath': driver})
    #
    #     if 300 > response.status_code >= 200:
    #         self._driver = dict(response.json())
    #     else:
    #         response.raise_for_status()

    '''Initializes Picoscope'''

    def _initialize_picoscope(self):
        # string passed through in VISA form
        print("Connecting to Picoscope instrument...")
        ps = ps6000.PS6000(serialNumber=None, connect=True)
        return ps

    '''destructor - close picoscope'''

    def __del__(self):
        print("closing Picoscope...")
        self._close()

    '''Closes Picoscope. Should be called when done using PicoscopeManager'''

    def _close(self):
        # self._ps.stop()
        self._ps.close()

    @property
    def name(self):
        return self._name

    @property
    def quantities(self):
        return self._driver['quantities']

    '''Set's default value for given quantity'''

    def _set_default_value(self, quantity):
        if self.quantities[quantity]['def_value']:
            self[quantity] = self.quantities[quantity]['def_value']

    def get_value(self, quantity):
        url = r'http://localhost:5000/instrumentDB/getLatestValue'
        response = requests.get(url, params={'cute_name': self._name, 'label': quantity})
        if 300 > response.status_code <= 200:
            # success
            pass
        else:
            response.raise_for_status()

        value = response.json()
        if value['latest_value'] is None:
            return self.quantities[quantity]['def_value']
        else:
            return value['latest_value']

    def set_value(self, quantity, value):
        self._check_limits(quantity, value)
        url = r'http://localhost:5000/instrumentDB/setLatestValue'
        response = requests.put(url, params={'cute_name': self._name, 'label': quantity, 'latest_value': value})
        if 300 > response.status_code <= 200:
            # success
            pass
        else:
            response.raise_for_status()

    def _check_limits(self, quantity, value):
        """Checks value against the limits or state values (for a combo) of a quantity
            Parameters:
                quantity -- qunatity whose limit to compare
                value -- value to compare against
            Raises:
                ValueError if value is out of range of limit or not in one of the combos states
        """

        lower_lim = self._driver['quantities'][quantity]['low_lim']
        upper_lim = self._driver['quantities'][quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        # check for valid states for Combos
        if self._driver['quantities'][quantity]['data_type'].upper() == 'COMBO':
            if self._driver['quantities'][quantity]['combo_cmd']:
                valid_states = list(self._driver['quantities'][quantity]['combo_cmd'].keys())
                valid_cmds = list(self._driver['quantities'][quantity]['combo_cmd'].values())
            else:
                raise ValueError(
                    f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.")

            if value not in (valid_states or valid_cmds):
                raise ValueError(
                    f"{value} is not a recognized state of {quantity}'s states. Valid states are {valid_states}.")

    def _convert_value(self, quantity, value):
        """Converts given value to pre-defined value in driver or returns the given value is N/A to convert
            Parameters:
                quantity -- quantity that holds the pre-defined value
                value -- value that needs converting
            Returns:
                Converted value
            Raises:
                ValueError if quantity is a boolean but a boolean value is not provided
        """
        quantity_dict = self._driver['quantities'][quantity]

        # change boolean values to driver specified boolean values
        # Checks allow for user to pass in TRUE, FALSE, or driver-defined values
        if quantity_dict['data_type'].upper() == 'BOOLEAN':
            if value.upper() == ("TRUE" or self._driver['visa']['str_true'].upper()):
                return self._driver['visa']['str_true']
            elif value.upper() == ("FALSE" or self._driver['visa']['str_false'].upper()):
                return self._driver['visa']['str_false']
            else:
                raise ValueError(f"{value} is not a valid boolean value.")

        elif quantity_dict['data_type'].upper() == 'COMBO':
            # combo quantity contains no states or commands
            if not quantity_dict['combo_cmd']:
                raise ValueError(
                    f"Quantity {quantity} of type 'COMBO' has no associated states or commands. Please update the driver and reupload to the Instrument Server.") \
 \
                    # if user provided name of the state, convert, else return given value as it is already a valid value for the commandcommand
            if value in quantity_dict['combo_cmd'].keys():
                return quantity_dict['combo_cmd'][value]

        else:
            return value

    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _signal_generator(self):
        pass
    # will be implemented in custom driver

    def _arbitrary_waveform_generator(self, frequency, waveformAmplitude, waveformOffset):
        pass
    # will be implemented in custom driver
