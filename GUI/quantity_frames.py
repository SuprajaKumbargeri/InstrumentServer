from PyQt6 import QtWidgets as QtW, QtCore, QtGui

class QuantityFrame(QtW.QFrame):
    def __init__(self, quantity_info: dict(dict), set_value_method: function, get_value_method: function):
        super().__init__()
        self.quantity_info = quantity_info
        self.set_value_method = set_value_method
        self.get_value_method = get_value_method
        
        # all QuantityFrames will have set and get buttons
        self.set_value_btn = QtW.QPushButton("Set value")
        self.set_value_btn.clicked.connect(self.set_value)
        self.get_value_btn = QtW.QPushButton("Get value")
        self.get_value_btn.clicked.connect(self.get_value)

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
    pass


class ButtonFrame(QuantityFrame):
    pass


class ComboFrame(QuantityFrame):
    def __init__(self, quantity_info: dict(dict), set_value_method: function, get_value_method: function):
        super().__init__(quantity_info, set_value_method, get_value_method)

        v_layout = QtW.QVBoxLayout()
        h_layout = QtW.QHBoxLayout()

        self.label = QtW.QLabel()
        self.label.setText(quantity_info["name"])
        v_layout.addWidget()

        self.combo_box = QtW.QComboBox()
        self.combo_box.addItems(quantity_info['combos'])

        h_layout.addWidget(self.combo_box)
        h_layout.addWidget(self.set_value_btn)
        h_layout.addWidget(self.get_value_btn)
        v_layout.addChildLayout(h_layout)

        self.setLayout(v_layout)

    @QuantityFrame.value.getter
    def value(self):
        return self.combo_box.currentText()
    
    def handle_incoming_value(self, value):
        self.combo_box.setCurrentText(value)

class ComplexFrame(QuantityFrame):
    pass


class DoubleFrame(QuantityFrame):
    def __init__(self, quantity_info, set_value_method: function, get_value_method: function):
        super().__init__()

        self.quantity_info = quantity_info
        self.set_value_method = set_value_method
        self.get_value_method = get_value_method

        v_layout = QtW.QVBoxLayout()
        h_layout = QtW.QHBoxLayout()

        self.label = QtW.QLabel()
        self.label.setText(quantity_info["name"])
        v_layout.addWidget()

        self.spin_box = QtW.QDoubleSpinBox()

        # Set min/max. Floats can handle '+-INF'
        min = float(quantity_info["low_lim"])
        max = float(quantity_info["max_lim"])
        self.spin_box.setMinimum(min)
        self.spin_box.setMaximum(max)
        
        self.set_value_btn = QtW.QPushButton("Set value")
        self.get_value_btn = QtW.QPushButton("Get value")

        h_layout.addWidget(self.spin_box)
        h_layout.addWidget(self.set_value_btn)
        h_layout.addWidget(self.get_value_btn)
        v_layout.addChildLayout(h_layout)

        self.setLayout(v_layout)
        

class PathFrame(QuantityFrame):
    pass


class StringFrame(QuantityFrame):
    pass


class VectorFrame(QuantityFrame):
    pass


class VectorComplexFrame(QuantityFrame):
    pass


def quantity_frame_factory(quantity_info):
    match quantity_info['data_type'].upper():
        case 'BOOLEAN':
            return BooleanFrame(quantity_info)
        case 'BUTTON':
            return ButtonFrame(quantity_info)
        case 'COMBO':
            return ComboFrame(quantity_info)
        case 'COMPLEX':
            return ComplexFrame(quantity_info)
        case 'DOUBLE':
            return DoubleFrame(quantity_info)
        case 'PATH':
            return PathFrame(quantity_info)
        case 'STRING':
            return StringFrame(quantity_info)
        case 'VECTOR':
            return VectorFrame(quantity_info)
        case 'VECTOR_COMPLEX':
            return VectorComplexFrame(quantity_info)
        
