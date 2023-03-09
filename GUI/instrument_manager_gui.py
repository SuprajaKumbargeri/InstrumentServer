from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea)
from Insrument.instrument_manager import InstrumentManager
from GUI.quantity_group_boxes import *

class InstrumentManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(InstrumentManagerGUI, self).__init__()

        scroll_layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(scroll_layout)

        # add all quantities
        for quantity in instrument_manager.quantity_names:
            quantity_info = instrument_manager.get_quantity_info(quantity)
            group = quantity_group_box_factory(quantity_info, instrument_manager.set_value, instrument_manager.get_value)
            group.setFixedHeight(100)
            scroll_layout.addWidget(group)

        scroll_layout.addStretch(1)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.setWindowTitle(f"{instrument_manager.name} Manager")
        self.show()
        self.resize(800, 600)


