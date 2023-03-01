from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QDoubleSpinBox, QMessageBox)
from PyQt6 import QtCore
from Insrument.instrument_manager import InstrumentManager
from GUI.quantity_frames import *

class QuantityManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(QuantityManagerGUI, self).__init__()

        self.im = instrument_manager
        self.main_layout = QVBoxLayout()
        
        quantity_info = self.im.get_quantity_info('Frequency')
        frame = quantity_frame_factory(quantity_info, self.im.set_value, self.im.get_value)
        self.main_layout.addWidget(frame)
        
        quantity_info = self.im.get_quantity_info('Function')
        frame = quantity_frame_factory(quantity_info, self.im.set_value, self.im.get_value)
        self.main_layout.addWidget(frame)

        self.setLayout(self.main_layout)

        self.setWindowTitle(f"{self.im.name} Quantity Manager")
        self.show()

        self.resize(800, 600)


