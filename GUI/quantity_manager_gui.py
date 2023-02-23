
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QComboBox, 
                             QPushButton)
from Insrument.instrument_manager import InstrumentManager


class QuantityManagerGUI(QMainWindow):
    def __init__(self, parent_gui: QMainWindow, instrument_manager: InstrumentManager):
        super().__init__()
        self._im = instrument_manager

        self.parent_gui = parent_gui
        self.setWindowTitle(f'{self._im.name} Quantity Manager')
        self.resize(500, 400)

        # This is the outermost widget or the "main" widget
        self.main_widget = QWidget()
        # The "top most" layout is vertical box layout (top -> bottom)
        self.main_layout = QHBoxLayout()
        
        quantities_combo = QComboBox()
        quantities_combo.addItems(self._im.quantity_names)
        self.main_layout.addWidget(quantities_combo)

        update_btn = QPushButton("Update Value")
        self.main_layout.addWidget(update_btn)

        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        
    