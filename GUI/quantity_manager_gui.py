from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QDoubleSpinBox)
from PyQt6 import QtCore
from Insrument.instrument_manager import InstrumentManager


class QuantityManagerGUI(QMainWindow):
    def __init__(self, parent_gui: QMainWindow, instrument_manager: InstrumentManager):
        super().__init__()
        self.im = instrument_manager

        self.parent_gui = parent_gui
        self.setWindowTitle(f'{self.im.name} Quantity Manager')
        self.resize(400, 200)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        self.quantities_combo = QComboBox()
        self.quantities_combo.addItems(self.im.quantity_names)
        self.quantities_combo.currentTextChanged.connect(self.quantity_selected_changed)
        self.main_layout.addWidget(self.quantities_combo)

        self.quantity_value_layout = QHBoxLayout()
        # Build layout for default selected quantity 
        self.quantity_selected_changed(self.quantities_combo.currentText())
        self.main_layout.addChildLayout(self.quantity_value_layout)

        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    @QtCore.pyqtSlot(str)
    def quantity_selected_changed(self, quantity):
        """Rebuilds quantity_value_layout when the user selects new quantity.
        quantity_value_layout display is changed dependent on the datatype of the quantity
        """
        self.clear_layout(self.quantity_value_layout)

        print(quantity)
        quantity_info = self.im.get_quantity_info(quantity)

        # 'DOUBLE', 'BOOLEAN', 'COMBO', 'STRING', 'COMPLEX',
        # 'VECTOR', 'VECTOR_COMPLEX', 'PATH', 'BUTTON'
        match quantity_info['data_type'].upper():
            case 'BOOLEAN':
                pass
            case 'BUTTON':
                pass
            case 'COMBO':
                self.build_combo_layout(quantity_info)
            case 'COMPLEX':
                pass
            case 'DOUBLE':
                self.build_double_layout(quantity_info)
            case 'PATH':
                pass
            case 'STRING':
                pass
            case 'VECTOR':
                pass
            case 'VECTOR_COMPLEX':
                pass

    # Clearing widgets and their layouts is weird
    # Check here: https://stackoverflow.com/a/13103617 for more info
    def clear_layout(self, layout):
        """Clears a layout/widget of any children"""
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)

    def build_combo_layout(self, quantity_info):
        self.combo = QComboBox()
        self.combo.addItems(quantity_info['combos'])
        self.quantity_value_layout.addWidget(self.combo)

        self.set_value_btn = QPushButton("Set Value")
        self.set_value_btn.clicked.connect(self.set_combo_value)
        self.quantity_value_layout.addWidget(self.set_value_btn)

        self.get_value_btn = QPushButton("Get Value")
        self.get_value_btn.clicked.connect(self.get_combo_value)
        self.quantity_value_layout.addWidget(self.get_value_btn)
        
    def set_combo_value(self):
        pass
        
    def get_combo_value(self):
        pass

    def build_double_layout(self, quantity_info):
        self.double = QDoubleSpinBox()
        self.quantity_value_layout.addWidget(self.quantities_combo)

        # defining settings for QDoubleSpinBox
        # TODO: Change to current value once DB has correct info
        self.double.setValue(float(quantity_info['def_value']))
        self.double.setSuffix(quantity_info['unit'])

        if quantity_info['low_lim'] != '-INF':
            self.double.minimum(float(quantity_info['low_lim']))
        if quantity_info['high_lim'] != '+INF':
            self.double.maximum(float(quantity_info['high_lim']))

        self.set_value_btn = QPushButton("Set Value")
        self.set_value_btn.clicked.connect(self.set_double_value)
        self.quantity_value_layout.addWidget(self.set_value_btn)

        self.get_value_btn = QPushButton("Get Value")
        self.get_value_btn.clicked.connect(self.get_double_value)
        self.quantity_value_layout.addWidget(self.get_value_btn)

    def set_double_value(self):
        pass
        
    def get_double_value(self):
        pass
    
