from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QDoubleSpinBox, QMessageBox)
from PyQt6 import QtCore
from Insrument.instrument_manager import InstrumentManager


class QuantityManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(QuantityManagerGUI, self).__init__()

        self.im = instrument_manager
        self.main_layout = QVBoxLayout()
        


