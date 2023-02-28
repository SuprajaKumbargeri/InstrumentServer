from PyQt6 import QtWidgets as QtW, QtCore, QtGui

class BooleanFrame(QtW.QFrame):
    pass


class ButtonFrame(QtW.QFrame):
    pass


class ComboFrame(QtW.QFrame):
    pass


class ComplexFrame(QtW.QFrame):
    pass


class DoubleFrame(QtW.QFrame):
    def __init__(self, quantity_info):
        super().__init__()

        self.quantity_info = quantity_info

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
        
        
