from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea)
from Insrument.instrument_manager import InstrumentManager
from GUI.quantity_group_boxes import *

class InstrumentManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(InstrumentManagerGUI, self).__init__()
        self.quantity_groups = list()

        scroll_layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(scroll_layout)

        # add all quantities
        for quantity in instrument_manager.quantity_names:
            quantity_info = instrument_manager.get_quantity_info(quantity)
            group = quantity_group_box_factory(quantity_info, instrument_manager.set_value,
                                               instrument_manager.get_value, self.handle_combo_change)
            group.setFixedHeight(100)
            scroll_layout.addWidget(group)
            self.quantity_groups.append(group)

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

    def handle_combo_change(self, quantity_name, state_value):
        for quantity_group in self.quantity_groups:
            if quantity_group.state_quant != quantity_name:
                continue

            if state_value in quantity_group.state_values:
                quantity_group.setHidden(False)
            else:
                quantity_group.setHidden(True)

