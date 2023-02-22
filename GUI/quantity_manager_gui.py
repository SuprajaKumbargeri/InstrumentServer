from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from Insrument.instrument_manager import InstrumentManager


class QuantityManagerGUI(QMainWindow):
    def __init__(self, parent_gui: QMainWindow, instrument_manager: InstrumentManager, quantity: str):
        super().__init__()
        self._im = instrument_manager

        self.parent_gui = parent_gui
        self.setWindowTitle(f'{quantity} Manager: {self._im.get_value(quantity)}')
        self.resize(500, 400)

        # This is the outermost widget or the "main" widget
        self.main_widget = QWidget()
        # The "top most" layout is vertical box layout (top -> bottom)
        self.main_layout = QHBoxLayout()
        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)

