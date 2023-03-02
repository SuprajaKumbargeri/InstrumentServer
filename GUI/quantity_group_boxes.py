from PyQt6 import QtWidgets as QtW
from PyQt6.QtGui import QFont
from typing import Callable

class QuantityGroupBox(QtW.QGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__()
        self.quantity_info = quantity_info
        self.set_value_method = set_value_method
        self.get_value_method = get_value_method

        self.v_layout = QtW.QVBoxLayout()

        self.label = QtW.QLabel()
        self.label.setText(quantity_info["name"])
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setMaximumHeight(25)
        self.v_layout.addWidget(self.label)

        self.h_layout = QtW.QHBoxLayout()
        self.h_frame = QtW.QFrame()
        
        # all QuantityGroupBoxs will have set and get buttons
        self.set_value_btn = QtW.QPushButton("Set value")
        self.set_value_btn.clicked.connect(self.set_value)
        self.set_value_btn.setMaximumHeight(25)
        self.get_value_btn = QtW.QPushButton("Get value")
        self.get_value_btn.clicked.connect(self.get_value)
        self.get_value_btn.setMaximumHeight(25)

    @property
    def value(self):
        """Returns current value of the quantity by the given QWidget. Should be implemented by child class"""
        raise NotImplementedError()

    def set_value(self):
        self.set_value_method(self.quantity_info['name'], self.value)

    def get_value(self):
        try:
            value = self.get_value_method(self.quantity_info['name'])
            self.handle_incoming_value(value)
        except Exception as e:
            print(e)
            QtW.QMessageBox.critical(self, 'Error', e)

    def handle_incoming_value(self, value):
        """Handles any value returned by instrument to be properly displayed. Should be implemented by child class"""
        raise NotImplementedError()


class BooleanGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)

        # Create butto group and connect to method
        self.group = QtW.QButtonGroup()
        self.group.setExclusive(False)
        self.group.buttonClicked.connect(self.radio_button_clicked)

        # add radio buttons to group
        self.true_radio_button = QtW.QRadioButton("True")
        self.group.addButton(self.true_radio_button)
        self.false_radio_button = QtW.QRadioButton("False")
        self.group.addButton(self.false_radio_button)

        self.h_layout.addWidget(self.true_radio_button)
        self.h_layout.addWidget(self.false_radio_button)
        self.h_layout.addWidget(self.set_value_btn)
        self.h_layout.addWidget(self.get_value_btn)

        self.h_frame.setLayout(self.h_layout)
        self.v_layout.addWidget(self.h_frame)
        self.setLayout(self.v_layout)

        # set quantity value to default value
        self.handle_incoming_value(bool(self.quantity_info['def_value']))

    def radio_button_clicked(self, radio_button):
        for button in self.group.buttons():
            if button is not radio_button:
                button.setChecked(False)

    @QuantityGroupBox.value.getter
    def value(self):
        return self.true_radio_button.isChecked()
    
    def handle_incoming_value(self, value):
        self.true_radio_button.setChecked(value)
        self.false_radio_button.setChecked(not value)


class ButtonGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class ComboGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)

        self.combo_box = QtW.QComboBox()
        self.combo_box.addItems(quantity_info['combos'])

        self.h_layout.addWidget(self.combo_box)
        self.h_layout.addWidget(self.set_value_btn)
        self.h_layout.addWidget(self.get_value_btn)

        self.h_frame.setLayout(self.h_layout)
        self.v_layout.addWidget(self.h_frame)

        self.setLayout(self.v_layout)

    @QuantityGroupBox.value.getter
    def value(self):
        return self.combo_box.currentText()
    
    def handle_incoming_value(self, value):
        self.combo_box.setCurrentText(value)


class ComplexGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class DoubleGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)

        self.spin_box = QtW.QDoubleSpinBox()

        # Set min/max. Floats can handle '+-INF'
        min = float(quantity_info["low_lim"])
        max = float(quantity_info["high_lim"])
        self.spin_box.setMinimum(min)
        self.spin_box.setMaximum(max)
        self.spin_box.setSuffix(quantity_info['unit'])

        self.h_layout.addWidget(self.spin_box)
        self.h_layout.addWidget(self.set_value_btn)
        self.h_layout.addWidget(self.get_value_btn)

        self.h_frame.setLayout(self.h_layout)
        self.v_layout.addWidget(self.h_frame)

        self.setLayout(self.v_layout)

        # set quantity value to default value
        self.handle_incoming_value(float(self.quantity_info['def_value']))

    @QuantityGroupBox.value.getter
    def value(self):
        return self.spin_box.value()
    
    def handle_incoming_value(self, value):
        self.spin_box.setValue(float(value))
        

class PathGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class StringGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class VectorGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class VectorComplexGroupBox(QuantityGroupBox):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


def quantity_group_box_factory(quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
    match quantity_info['data_type'].upper():
        case 'BOOLEAN':
            return BooleanGroupBox(quantity_info, set_value_method, get_value_method)
        case 'BUTTON':
            return ButtonGroupBox(quantity_info, set_value_method, get_value_method)
        case 'COMBO':
            return ComboGroupBox(quantity_info, set_value_method, get_value_method)
        case 'COMPLEX':
            return ComplexGroupBox(quantity_info, set_value_method, get_value_method)
        case 'DOUBLE':
            return DoubleGroupBox(quantity_info, set_value_method, get_value_method)
        case 'PATH':
            return PathGroupBox(quantity_info, set_value_method, get_value_method)
        case 'STRING':
            return StringGroupBox(quantity_info, set_value_method, get_value_method)
        case 'VECTOR':
            return VectorGroupBox(quantity_info, set_value_method, get_value_method)
        case 'VECTOR_COMPLEX':
            return VectorComplexGroupBox(quantity_info, set_value_method, get_value_method)
        
