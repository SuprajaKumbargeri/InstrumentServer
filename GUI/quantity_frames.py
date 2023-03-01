from PyQt6 import QtWidgets as QtW, QtCore, QtGui
from typing import Callable

class QuantityFrame(QtW.QFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__()
        self.quantity_info = quantity_info
        self.set_value_method = set_value_method
        self.get_value_method = get_value_method

        self.label = QtW.QLabel()
        self.label.setText(quantity_info["name"])
        self.label.setMaximumHeight(25)

        self.v_layout = QtW.QVBoxLayout()
        self.v_layout.setContentsMargins(0,0,0,0)
        self.h_layout = QtW.QHBoxLayout()
        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_frame = QtW.QFrame()
        
        # all QuantityFrames will have set and get buttons
        self.set_value_btn = QtW.QPushButton("Set value")
        self.set_value_btn.clicked.connect(self.set_value)
        self.set_value_btn.setMaximumHeight(25)
        
        self.get_value_btn = QtW.QPushButton("Get value")
        self.get_value_btn.clicked.connect(self.get_value)
        self.get_value_btn.setMaximumHeight(25)

    @property
    def value(self):
        raise NotImplementedError()

    def set_value(self):
        self.set_value_method(self.quantity_info['name'], self.value)

    def get_value(self):
        try:
            value = self.get_value_method(self.quantity_info['name'])
            self.handle_incoming_value(value)
        except Exception as e:
            QtW.QMessageBox.critical(self, 'Error', e)

    def handle_incoming_value(self):
        raise NotImplementedError()


class BooleanFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class ButtonFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class ComboFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)

        self.label = QtW.QLabel()
        self.label.setText(quantity_info["name"])
        self.v_layout.addWidget(self.label)

        self.combo_box = QtW.QComboBox()
        self.combo_box.addItems(quantity_info['combos'])

        self.h_layout.addWidget(self.combo_box)
        self.h_layout.addWidget(self.set_value_btn)
        self.h_layout.addWidget(self.get_value_btn)

        self.h_frame.setLayout(self.h_layout)
        self.v_layout.addWidget(self.h_frame)

        self.setLayout(self.v_layout)

    @QuantityFrame.value.getter
    def value(self):
        return self.combo_box.currentText()
    
    def handle_incoming_value(self, value):
        self.combo_box.setCurrentText(value)


class ComplexFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class DoubleFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)

        self.v_layout.addWidget(self.label)

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

    @QuantityFrame.value.getter
    def value(self):
        return self.spin_box.value()
    
    def handle_incoming_value(self, value):
        self.spin_box.setValue(value)
        

class PathFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class StringFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class VectorFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


class VectorComplexFrame(QuantityFrame):
    def __init__(self, quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
        super().__init__(quantity_info, set_value_method, get_value_method)


def quantity_frame_factory(quantity_info: dict[dict], set_value_method: Callable, get_value_method: Callable):
    match quantity_info['data_type'].upper():
        case 'BOOLEAN':
            return BooleanFrame(quantity_info, set_value_method, get_value_method)
        case 'BUTTON':
            return ButtonFrame(quantity_info, set_value_method, get_value_method)
        case 'COMBO':
            return ComboFrame(quantity_info, set_value_method, get_value_method)
        case 'COMPLEX':
            return ComplexFrame(quantity_info, set_value_method, get_value_method)
        case 'DOUBLE':
            return DoubleFrame(quantity_info, set_value_method, get_value_method)
        case 'PATH':
            return PathFrame(quantity_info, set_value_method, get_value_method)
        case 'STRING':
            return StringFrame(quantity_info, set_value_method, get_value_method)
        case 'VECTOR':
            return VectorFrame(quantity_info, set_value_method, get_value_method)
        case 'VECTOR_COMPLEX':
            return VectorComplexFrame(quantity_info, set_value_method, get_value_method)
        
