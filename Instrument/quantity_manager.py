from __future__ import annotations
from typing import Callable
import requests


class QuantityManager:
    def __init__(self, quantity_info: dict, write_method: Callable, read_method: Callable, str_true, str_false, logger=None):
        self.instrument_name = quantity_info['cute_name']
        self.name = quantity_info['label']
        self.data_type = quantity_info['data_type'].upper()
        self.unit = quantity_info['unit']
        self.default_value = quantity_info['def_value']
        self.tool_tip = quantity_info['tool_tip']
        self.low_lim = float(quantity_info['low_lim'])
        self.high_lim = float(quantity_info['high_lim'])
        self.x_name = quantity_info['x_name']
        self.x_unit = quantity_info['x_unit']
        self.combo_cmd = quantity_info['combo_cmd']
        self.groupname = quantity_info['groupname']
        self.section = quantity_info['section']
        self.state_quant = quantity_info['state_quant']
        self.state_values = quantity_info['state_values']
        self.model_values = quantity_info['model_values']
        self.option_values = quantity_info['option_values']
        self.permission = quantity_info['permission']
        self.show_in_measurement_dlg = quantity_info['show_in_measurement_dlg']
        self.set_cmd = str(quantity_info['set_cmd'])
        self.get_cmd = str(quantity_info['get_cmd'])
        self.latest_value = quantity_info['latest_value']
        self.is_visible = True

        self._write_method = write_method
        self._read_method = read_method
        self.str_true = str_true
        self.str_false = str_false

        # If quantity is linked to another, when get/set are called, it calls the corresponding linked quantity instead
        self.linked_quantity_get: QuantityManager = None
        self.linked_quantity_set: QuantityManager = None

    # region set_value methods
    def set_value(self, value):
        """Sets quantity value to <value>"""
        if self.linked_quantity_set:
            self.linked_quantity_set.set_latest_value(value)
            return
        
        value = self.convert_value(value)

        # add the value to the command and write to instrument
        cmd = self.set_cmd
        if "<*>" in cmd:
            cmd = cmd.replace("<*>", str(value))
        else:
            cmd += f' {value}'


        value = self.convert_value(value)
        # add the value to the command and write to instrument
        cmd = self.set_cmd
        if "<*>" in cmd:
            cmd = cmd.replace("<*>", str(value))
        else:
            cmd += f' {value}'

        self._write_method(cmd)
        self.latest_value = value

    def set_default_value(self):
        """Sets quantity value to default value as defined in driver"""
        if self.linked_quantity_set:
            self.linked_quantity_set.set_default_value()
            return

        self.set_value(self.default_value)

    def set_latest_value(self, value):
        """Sets quantity's latest_value in database to <value>"""
        if self.linked_quantity_set:
            self.linked_quantity_set.set_latest_value(value)
            return

        self.latest_value = value

        # send to server
        url = r'http://127.0.0.1:5000/instrumentDB/setLatestValue'
        response = requests.put(url, params={
            'cute_name': self.instrument_name, 'label': self.name, 'latest_value': value})
        if response.status_code >= 300:
            response.raise_for_status()
    # endregion

    # region get_value methods
    def get_value(self):
        """Returns quantity value in user form"""
        if self.linked_quantity_get:
            return self.linked_quantity_get.get_value()

        self._write_method(self.get_cmd)
        value = self._read_method()

        # update latest value
        self.set_latest_value(value)
        return self.convert_return_value(value)

    def get_latest_value(self):
        """Returns quantity latest_value in database in user form"""
        if self.linked_quantity_get:
            return self.linked_quantity_get.get_latest_value()

        # query server
        url = r'http://127.0.0.1:5000/instrumentDB/getLatestValue'
        response = requests.get(url, params={'cute_name': self.instrument_name, 'label': self.name})

        if 300 > response.status_code >= 200:
            self.latest_value = dict(response.json())['latest_value']
            return self.latest_value
        else:
            response.raise_for_status()
    # endregion

    def convert_value(self, value):
        """Converts given value from user form to command form
            Raises: ValueError
        """

        if self.data_type == 'BOOLEAN':
            value = str(value).strip()

            if value.upper() in ("TRUE", self.str_true.upper()):
                return self.str_true
            elif value.upper() in ("FALSE", self.str_false.upper()):
                return self.str_false
            else:
                raise ValueError(f"{value} is not a valid boolean value.")

        # Check Combo values
        elif self.data_type == 'COMBO':
            value = value.strip()

            # combo quantity contains no states or commands
            if not self.combo_cmd:
                raise ValueError(
                    f"Quantity {self.name} of type 'COMBO' has no associated states or commands. Please update the "
                    f"driver and reupload to the Instrument Server.")

                # if user provided name of the state, convert it to command value
            if value in (combo.strip() for combo in self.combo_cmd.keys()):
                return self.combo_cmd[value]
            # return given value as it is already a valid value for the command
            elif value in (combo.strip() for combo in self.combo_cmd.values()):
                return value
            # incorrect value given, raise error
            else:
                raise ValueError(f"Quantity '{self.name}' of type 'COMBO' has no ")

        else:
            return value

    def convert_return_value(self, value):
        """Converts given value from command form to user form
            Raises: ValueError
        """

        # change driver specified boolean values to boolean value
        if self.data_type == 'BOOLEAN':
            value = str(value).strip()
            if value in (self.str_true.upper(), str(True)):
                return True
            elif value in (self.str_false.upper(), str(False)):
                return False
            else:
                raise ValueError(f"{self.name} returned an invalid value for {self.instrument_name}. "
                                 f"{value} is not a valid boolean value. Please check instrument driver.")

        # Instrument will return instrument-defined value, convert it to driver-defined value
        elif self.data_type == 'COMBO':
            value = value.strip()

            # key contains driver-defined value, cmd contains instrument-defined value
            # need to return driver-defined value
            for key, cmd in self.combo_cmd.items():
                if value in (key.strip(), cmd.strip()):
                    return key

            raise ValueError(
                f"{self.name} returned an invalid value for {self.name}. "
                f"{value} is not a valid combo value. Please check instrument driver.")

        else:
            return value

    # region private helper methods
    def _check_limits(self, value):
        """Checks value against the limits or state values (for a combo) of a quantity
                    Parameters:
                        quantity -- qunatity whose limit to compare
                        value -- value to compare against
                    Raises:
                        ValueError if value is out of range of limit or not in one of the combos states
                """

        # check limits for DOUBLE
        if self.data_type == "DOUBLE":
            if value < self.low_lim:
                raise ValueError(f"{value} is lower than {self.name}'s lower limit of {self.low_lim}.")
            if value > float(self.high_lim):
                raise ValueError(f"{value} is higher than {self.name}'s upper limit of {self.high_lim}.")

        # check for valid states for COMBO
        if self.data_type == 'COMBO':
            if self.combo_cmd:
                valid_states = list(self.combo_cmd.keys())
                valid_cmds = list(self.combo_cmd.values())
            else:
                raise ValueError(
                    f"Quantity {self.name} of type 'COMBO' has no associated states or commands. "
                    f"Please update the driver and reupload to the Instrument Server.")

            if value not in valid_states and value not in valid_cmds:
                raise ValueError(
                    f"{value} is not a recognized state of {self.name}'s states. Valid states are {valid_states}.")
    # endregion
