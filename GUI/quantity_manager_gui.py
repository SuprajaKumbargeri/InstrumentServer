from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QDoubleSpinBox, QMessageBox)
from PyQt6 import QtCore
from Insrument.instrument_manager import InstrumentManager


class QuantityManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(QuantityManagerGUI, self).__init__()

        self.im = instrument_manager
        self.main_layout = QVBoxLayout()
        self.quantity_value_layout = None
        
        self.quantity_combo = QComboBox()
        self.quantity_combo.addItems(self.im.quantity_names)
        self.quantity_combo.currentTextChanged.connect(self.quantity_selected_changed)
        self.main_layout.addWidget(self.quantity_combo)

        self.init_double_frame()
        self.main_layout.addWidget(self.double_frame)

        self.setFixedSize(500, 200)
        self.setWindowTitle(f"{self.im.name} Manager")
        self.setLayout(self.main_layout)
        self.show()

        self.quantity_selected_changed(self.quantity_combo.currentText())

    def init_double_frame(self):
        self.double_frame = QFrame()
        h_layout = QHBoxLayout()

        self.double_spinbox = QDoubleSpinBox()
        self.double_spinbox.setFixedSize(250, 25)
        h_layout.addWidget(self.double_spinbox)
        
        self.set_double_value_btn = QPushButton("Set value")
        self.set_double_value_btn.clicked.connect(self.set_double_value_btn_clicked)
        self.set_double_value_btn.setFixedSize(100, 25)
        h_layout.addWidget(self.set_double_value_btn)
        
        self.get_double_value_btn = QPushButton("Get value")
        self.get_double_value_btn.clicked.connect(self.get_double_value_btn_clicked)
        self.get_double_value_btn.setFixedSize(100, 25)
        h_layout.addWidget(self.get_double_value_btn)
    
        self.double_frame.setLayout(h_layout)

    @QtCore.pyqtSlot(str)
    def quantity_selected_changed(self, quantity):
        """Rebuilds quantity_value_layout when the user selects new quantity.
        quantity_value_layout display is changed dependent on the datatype of the quantity
        """
        self.hide_all_frames()

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
                pass
            case 'COMPLEX':
                pass
            case 'DOUBLE':
                self.double_frame.show()
                self.set_double_quantity_parameters(quantity_info)
            case 'PATH':
                pass
            case 'STRING':
                pass
            case 'VECTOR':
                pass
            case 'VECTOR_COMPLEX':
                pass

    def hide_all_frames(self):
        self.double_frame.hide()


    def set_double_quantity_parameters(self, quantity_info):
        self.double_spinbox.setSuffix(quantity_info['unit'])

        # set upper limit
        if quantity_info['high_lim'] == '+INF':
            self.double_spinbox.setMaximum(1000000)
        else:
            self.double_spinbox.setMaximum(float(quantity_info['high_lim']))

        # set lower limit
        if quantity_info['low_lim'] == '-INF':
            self.double_spinbox.setMinimum(-1000000)
        else:
            self.double_spinbox.setMinimum(float(quantity_info['low_lim']))

        value = float(self.im.get_value(quantity_info['name']))
        self.double_spinbox.setValue(value)

    def set_double_value_btn_clicked(self):
        quantity = self.quantity_combo.currentText()
        value = self.double_spinbox.value()

        self.im.set_value(quantity, value)

    def get_double_value_btn_clicked(self):
        quantity = self.quantity_combo.currentText()
        value = self.im.get_value(quantity)
        unit = self.im.get_quantity_info(quantity)['unit']

        QMessageBox.information(self, '', f'The value of "{quantity}" is {value} {unit}')


