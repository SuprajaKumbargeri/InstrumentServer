from PyQt6 import QtCore, QtWidgets as QtW
from PyQt6.QtGui import QFont, QAction, QCursor
from typing import Callable
import logging


class QuantityFrame(QtW.QFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__()

        self.quantity_info = quantity_info
        self.get_value_method = get_value_method
        self.set_value_method = set_value_method
        self.set_def_val_method = set_def_val_method
        self.on_value_change = on_value_change
        self.logger = logger
        self.label_weight = 1
        self.value_weight = 2

        # Set basic layout
        self.layout = QtW.QHBoxLayout()
        self.label = QtW.QLabel()
        self.label.setText(quantity_info['label'])
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setMaximumHeight(25)
        self.layout.addWidget(self.label, self.label_weight)

        # Create menu for right click events
        # Implemented into widget by subclasses
        self.get_action = QAction('Query quantity value')
        self.set_def_val_action = QAction('Set default value')
        self.menu = QtW.QMenu()
        self.menu.addAction(self.get_action)
        self.menu.addAction(self.set_def_val_action)

        # TODO: Permission
        match self.quantity_info['permission'].upper():
            case 'NONE':
                pass
            case 'READ':
                pass
            case 'WRITE':
                pass
            # Both
            case _:
                pass

    @property
    def name(self):
        return self.quantity_info['name']

    @property
    def value(self):
        """Returns current value of the quantity by the given QWidget. Should be implemented by child class"""
        raise NotImplementedError()

    @property
    def state_quant(self):
        """Returns quantity that controls self's visibility"""
        return self.quantity_info['state_quant']

    @property
    def state_values(self):
        """Returns state values associated with state_quant for when self is visible"""
        return self.quantity_info['state_values']

    def custom_context_menu_event(self):
        action = self.menu.exec(QCursor.pos())
        if action == self.get_action:
            self.get_value()
        elif action == self.set_def_val_action:
            self.set_default_value()

    def get_value(self):
        try:
            value = self.get_value_method(self.quantity_info['name'])
            self.handle_incoming_value(value)
        except Exception as e:
            self.logger.error(f"Error querying '{self.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error querying '{self.name}'", str(e))

    def set_value(self):
        try:
            self.set_value_method(self.quantity_info['name'], self.value)
            self.on_value_change()
        except Exception as e:
            self.logger.error(f"Error setting '{self.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error setting '{self.name}'", str(e))

    def set_default_value(self):
        try:
            self.set_def_val_method(self.name)
        except Exception as e:
            self.logger.error(f"Error setting '{self.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error setting '{self.name}'", str(e))
        self.get_value()

    def handle_incoming_value(self, value):
        """Handles any value returned by instrument to be properly displayed. Should be implemented by child class"""
        raise NotImplementedError()


class BooleanFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)

        # Create button group and connect to method
        self.button_group = QtW.QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.set_value)

        # add radio buttons to group
        self.true_radio_button = QtW.QRadioButton("True")
        self.button_group.addButton(self.true_radio_button)
        self.true_radio_button.setToolTip(self.quantity_info['tool_tip'])
        self.false_radio_button = QtW.QRadioButton("False")
        self.button_group.addButton(self.false_radio_button)
        self.false_radio_button.setToolTip(self.quantity_info['tool_tip'])

        # create local layout and button group widget so that the spacing is correct
        h_layout = QtW.QHBoxLayout()
        h_layout.addWidget(self.true_radio_button)
        h_layout.addWidget(self.false_radio_button)

        self.button_group_widget = QtW.QWidget()
        self.button_group_widget.setLayout(h_layout)
        self.button_group_widget.setFixedHeight(40)

        # Implement context menu created in parent class
        self.button_group_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.button_group_widget.customContextMenuRequested.connect(self.custom_context_menu_event)

        self.layout.addWidget(self.button_group_widget, self.value_weight)
        self.setLayout(self.layout)

        # set quantity value to last known value in DB or default value
        if self.quantity_info['latest_value']:
            self.handle_incoming_value(bool(self.quantity_info['latest_value']))
        else:
            self.handle_incoming_value(bool(self.quantity_info['def_value']))

    @QuantityFrame.value.getter
    def value(self):
        return self.true_radio_button.isChecked()

    def handle_incoming_value(self, value):
        self.true_radio_button.setChecked(value)
        self.false_radio_button.setChecked(not value)
        self.on_value_change()


class ButtonFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


class ComboFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        self.on_value_change = on_value_change

        self.combo_box = QtW.QComboBox()
        self.combo_box.addItems(self.quantity_info['combos'])
        self.combo_box.setToolTip(self.quantity_info['tool_tip'])
        self.combo_box.currentIndexChanged.connect(self.set_value)

        # set context menu
        self.combo_box.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.combo_box.customContextMenuRequested.connect(self.custom_context_menu_event)

        self.layout.addWidget(self.combo_box, self.value_weight)
        self.setLayout(self.layout)

        # set quantity value to last known value in DB or default value
        if self.quantity_info['latest_value']:
            self.handle_incoming_value(self.quantity_info['latest_value'])
        else:
            self.handle_incoming_value(self.quantity_info['def_value'])

    @QuantityFrame.value.getter
    def value(self):
        return self.combo_box.currentText()

    def handle_incoming_value(self, value):
        self.combo_box.setCurrentText(value)
        self.on_value_change()


class ComplexFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


class DoubleFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)

        self.spin_box = QtW.QDoubleSpinBox()

        # Set min/max. Floats can handle '+-INF'
        low = float(quantity_info["low_lim"])
        high = float(quantity_info["high_lim"])
        self.spin_box.setMinimum(low)
        self.spin_box.setMaximum(high)

        self.spin_box.setSuffix(f" {self.quantity_info['unit']}")
        self.spin_box.setToolTip(self.quantity_info['tool_tip'])
        self.spin_box.valueChanged.connect(self.set_value)

        self.spin_box.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.spin_box.customContextMenuRequested.connect(self.custom_context_menu_event)

        self.layout.addWidget(self.spin_box, self.value_weight)
        self.setLayout(self.layout)

        # set quantity value to last known value in DB or default value
        if self.quantity_info['latest_value']:
            self.handle_incoming_value(float(self.quantity_info['latest_value']))
        else:
            self.handle_incoming_value(float(self.quantity_info['def_value']))

    @QuantityFrame.value.getter
    def value(self):
        return self.spin_box.value()

    def handle_incoming_value(self, value):
        self.spin_box.setValue(float(value))
        self.on_value_change()


class PathFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


class StringFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


class VectorFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        self.setLayout(self.layout)

    def set_default_value(self):
        pass


class VectorComplexFrame(QuantityFrame):
    def __init__(self, quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                 set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


def quantity_frame_factory(quantity_info: dict, get_value_method: Callable, set_value_method: Callable,
                           set_def_val_method: Callable, on_value_change: Callable, logger: logging.Logger,):
    match quantity_info['data_type'].upper():
        case 'BOOLEAN':
            return BooleanFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'BUTTON':
            return ButtonFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'COMBO':
            return ComboFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'COMPLEX':
            return ComplexFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'DOUBLE':
            return DoubleFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'PATH':
            return PathFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'STRING':
            return StringFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'VECTOR':
            return VectorFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)
        case 'VECTOR_COMPLEX':
            return VectorComplexFrame(quantity_info, get_value_method, set_value_method, set_def_val_method, on_value_change, logger)


class QuantityGroupBox(QtW.QGroupBox):
    def __init__(self, group_name: str, frames: list[QuantityFrame]):
        super().__init__()

        self.layout = QtW.QVBoxLayout()

        self.label = QtW.QLabel()
        self.label.setText(group_name)
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setMaximumHeight(25)
        self.layout.addWidget(self.label)

        for frame in frames:
            self.layout.addWidget(frame)

        self.setLayout(self.layout)
