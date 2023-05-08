from PyQt6 import QtCore, QtWidgets as QtW
from PyQt6.QtGui import QFont, QAction, QCursor
from typing import Callable, Optional
import logging

from Instrument.quantity_manager import QuantityManager
from Instrument.instrument_manager import InstrumentManager


class QuantityFrame(QtW.QFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__()

        self.quantity = quantity
        self.on_value_change = on_value_change
        self.logger = logger
        self.label_weight = 1
        self.value_weight = 2

        # Set basic layout
        self.layout = QtW.QHBoxLayout()
        self.label = QtW.QLabel()
        self.label.setText(quantity.name)
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
        match self.quantity.permission.upper():
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
    def value(self):
        """Returns current value of the quantity by the given QWidget. Should be implemented by child class"""
        raise NotImplementedError()

    def custom_context_menu_event(self):
        action = self.menu.exec(QCursor.pos())
        if action == self.get_action:
            self.get_value()
        elif action == self.set_def_val_action:
            self.set_default_value()

    def get_value(self):
        try:
            value = self.quantity.get_value()
            self.handle_incoming_value(value)
        except Exception as e:
            self.logger.error(f"Error querying '{self.quantity.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error querying '{self.quantity.name}'", str(e))

    def set_value(self):
        try:
            self.quantity.set_value(self.value)
            self.on_value_change(self.quantity.name, self.value)
        except Exception as e:
            self.logger.error(f"Error setting '{self.quantity.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error setting '{self.quantity.name}'", str(e))

    def set_default_value(self):
        try:
            self.quantity.set_default_value()
        except Exception as e:
            self.logger.error(f"Error setting '{self.quantity.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error setting '{self.quantity.name}'", str(e))
        self.get_value()

    def handle_incoming_value(self, value):
        """Handles any value returned by instrument to be properly displayed. Should be implemented by child class"""
        raise NotImplementedError()


class BooleanFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)

        # Create button group and connect to method
        self.button_group = QtW.QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.set_value)

        # add radio buttons to group
        self.true_radio_button = QtW.QRadioButton("True")
        self.button_group.addButton(self.true_radio_button)
        self.true_radio_button.setToolTip(self.quantity.tool_tip)
        self.false_radio_button = QtW.QRadioButton("False")
        self.button_group.addButton(self.false_radio_button)
        self.false_radio_button.setToolTip(self.quantity.tool_tip)

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
        if self.quantity.latest_value:
            self.handle_incoming_value(bool(self.quantity.latest_value))
        else:
            self.handle_incoming_value(bool(self.quantity.default_value))

    @QuantityFrame.value.getter
    def value(self):
        return self.true_radio_button.isChecked()

    def handle_incoming_value(self, value):
        self.true_radio_button.setChecked(value)
        self.false_radio_button.setChecked(not value)
        self.on_value_change(self.quantity.name, value)


class ButtonFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)


class ComboFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)
        self.on_value_change = on_value_change

        self.combo_box = QtW.QComboBox()
        self.combo_box.addItems(self.quantity.combo_cmd.keys())
        self.combo_box.setToolTip(self.quantity.tool_tip)
        self.combo_box.setToolTip(self.quantity.tool_tip)
        self.combo_box.currentIndexChanged.connect(self.set_value)

        # set context menu
        self.combo_box.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.combo_box.customContextMenuRequested.connect(self.custom_context_menu_event)

        self.layout.addWidget(self.combo_box, self.value_weight)
        self.setLayout(self.layout)

        # set quantity value to last known value in DB or default value
        if self.quantity.latest_value:
            self.handle_incoming_value(self.quantity.latest_value)
        else:
            self.handle_incoming_value(self.quantity.default_value)

    @QuantityFrame.value.getter
    def value(self):
        return self.combo_box.currentText()

    def handle_incoming_value(self, value):
        self.combo_box.setCurrentText(value)
        self.on_value_change(self.quantity.name, value)


class ComplexFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)


class DoubleFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)

        self.spin_box = QtW.QDoubleSpinBox()

        # Set min/max. Floats can handle '+-INF'
        low = float(quantity.low_lim)
        high = float(quantity.high_lim)
        self.spin_box.setMinimum(low)
        self.spin_box.setMaximum(high)

        self.spin_box.setSuffix(f" {self.quantity.unit}")
        self.spin_box.setToolTip(self.quantity.tool_tip)
        self.spin_box.valueChanged.connect(self.set_value)

        self.spin_box.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.spin_box.customContextMenuRequested.connect(self.custom_context_menu_event)

        self.layout.addWidget(self.spin_box, self.value_weight)
        self.setLayout(self.layout)

        # set quantity value to last known value in DB or default value
        if self.quantity.latest_value:
            self.handle_incoming_value(float(self.quantity.latest_value))
        else:
            self.handle_incoming_value(float(self.quantity.default_value))

    @QuantityFrame.value.getter
    def value(self):
        return self.spin_box.value()

    def handle_incoming_value(self, value):
        self.spin_box.setValue(float(value))
        self.on_value_change(self.quantity.name, value)


class PathFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)


class StringFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)


class VectorFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)
        self.setLayout(self.layout)

    def set_default_value(self):
        pass


class VectorComplexFrame(QuantityFrame):
    def __init__(self, quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger):
        super().__init__(quantity, on_value_change, logger)


def quantity_frame_factory(quantity: QuantityManager, on_value_change: Callable, logger: logging.Logger,):
    match quantity.data_type.upper():
        case 'BOOLEAN':
            return BooleanFrame(quantity, on_value_change, logger)
        case 'BUTTON':
            return ButtonFrame(quantity, on_value_change, logger)
        case 'COMBO':
            return ComboFrame(quantity, on_value_change, logger)
        case 'COMPLEX':
            return ComplexFrame(quantity, on_value_change, logger)
        case 'DOUBLE':
            return DoubleFrame(quantity, on_value_change, logger)
        case 'PATH':
            return PathFrame(quantity, on_value_change, logger)
        case 'STRING':
            return StringFrame(quantity, on_value_change, logger)
        case 'VECTOR':
            return VectorFrame(quantity, on_value_change, logger)
        case 'VECTOR_COMPLEX':
            return VectorComplexFrame(quantity, on_value_change, logger)


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


class LinkQuantityFrame(QtW.QFrame):
    def __init__(self, quantity: QuantityManager, instruments: dict[str: InstrumentManager]):
        super().__init__()

        self.quantity_manager = quantity
        self.connected_instruments = instruments

        layout = QtW.QVBoxLayout()
        h1_layout = QtW.QHBoxLayout()
        h2_layout = QtW.QHBoxLayout()

        self.instrument_combo = QtW.QComboBox()
        self.quantity_combo = QtW.QComboBox()

        h1_layout.addWidget(self.instrument_combo)
        h1_layout.addWidget(self.quantity_combo)

        self.link_set_checkbox = QtW.QCheckBox("Link for writes")
        self.link_get_checkbox = QtW.QCheckBox("Link for reads")

        self.initialize_widgets()

        h2_layout.addWidget(self.link_set_checkbox)
        h2_layout.addWidget(self.link_get_checkbox)
        widget1 = QtW.QWidget()
        widget2 = QtW.QWidget()
        widget1.setLayout(h1_layout)
        widget2.setLayout(h2_layout)
        layout.addWidget(widget1)
        layout.addWidget(widget2)
        self.setLayout(layout)

    def initialize_widgets(self):
        items = ["None"]
        items += list(self.connected_instruments.keys())
        self.instrument_combo.addItems(items)
        self.instrument_combo.currentTextChanged.connect(self.on_instrument_change)

        self.quantity_combo.addItem("None")

        # linked_wuant could be set twice, but will always be same quantity
        linked_quant = None
        # Set checkboxes to True if quantity is linked to read/write
        if self.quantity_manager.linked_quantity_set:
            linked_quant = self.quantity_manager.linked_quantity_set
            self.link_set_checkbox.setChecked(True)
        if self.quantity_manager.linked_quantity_get:
            linked_quant = self.quantity_manager.linked_quantity_get
            self.link_get_checkbox.setChecked(True)

        if linked_quant:
            # set instrument combo index to instrument of linked quantity
            self.instrument_combo.setCurrentText(linked_quant.instrument_name)
            # set quantity combo index to linked quantity
            self.quantity_combo.setCurrentText(linked_quant.name)

    def on_instrument_change(self):
        # clear all data from quantity combo
        self.quantity_combo.clear()
        self.quantity_combo.addItem("None")
        selected_instrument = self.selected_instrument

        if selected_instrument is None:
            return

        # Names of all visible quantities
        quantities = list(x.name for x in selected_instrument.get_visible_quantities())

        # This stops cyclical linking
        if selected_instrument.name == self.quantity_manager.instrument_name:
            quantities.remove(self.quantity_manager.name)

        self.quantity_combo.addItems(quantities)

    @property
    def selected_instrument(self) -> Optional[InstrumentManager]:
        if self.instrument_combo.currentText() == "None":
            return None
        return self.connected_instruments[self.instrument_combo.currentText()]

    @property
    def linked_quantity(self) -> Optional[QuantityManager]:
        selected_instrument = self.selected_instrument
        if selected_instrument is None or self.quantity_combo.currentText() == "None":
            return None

        return selected_instrument.quantities[self.quantity_combo.currentText()]

    @property
    def link_set(self):
        return self.link_set_checkbox.isChecked()

    @property
    def link_get(self):
        return self.link_get_checkbox.isChecked()
