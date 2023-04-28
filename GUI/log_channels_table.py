import logging
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import Callable
import json
     
class LogChannelsTreeWidget(QTreeWidget):
    def __init__(self, channels_added: dict(), item_valid: Callable, logger: logging.Logger):
        super().__init__()
        self.logger = logger

        # dictionary for added channels in the table
        self.channels_added = channels_added

        # dictionary for quantities of each added channel
        # key: (instrument_name, quantity_name)
        # value: TreeWidgetItems
        self.quantities_added = dict()

        self.item_valid = item_valid

        self.setDragEnabled(True) # TODO: Disable manual rearrangement
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
         # Disabling arrows in the Tree Widget
        self.setStyleSheet( "QTreeWidget::branch{border-image: url(none.png);}") # TODO: Remove

        # Tree Widget Items remain expanded, disabling the option to toggle expansion
        self.setItemsExpandable(False) # TODO: Remove

        # Allow only one selection at a time -> SingleSelection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        """
        Column Order:
        ['Quantity', 'Instrument', 'Address']
        """
        self.setHeaderLabels(['Channel', 'Instrument', 'Address'])
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.itemSelectionChanged.connect(self.log_channels_table_selection_changed)

    @property
    def quantities(self):
        return self.quantities_added.keys()

    def check_item_valid(self, instrument_name, quantity_name):
        # Check if the quantity already exists
        if (instrument_name, quantity_name) in self.quantities_added.keys():
            return False
        return True

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/json'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/json'):
            byte_data = event.mimeData().data('application/json')
            json_string = str(byte_data, 'utf-8')
            data_dict = json.loads(json_string)
            if self.item_valid(data_dict['instrument_name'], data_dict['quantity_name']):
                event.setDropAction(Qt.DropAction.CopyAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/json'):
            byte_data = event.mimeData().data('application/json')
            json_string = str(byte_data, 'utf-8')
            data_dict = json.loads(json_string)

            instrument_name = data_dict['instrument_name']
            quantity_name = data_dict['quantity_name']

            # TODO: Remove
            if (instrument_name, quantity_name) in self.quantities_added.keys():
                event.ignore()
                return
            
            item = QTreeWidgetItem(self, [quantity_name, instrument_name, ''])
            self.quantities_added[(instrument_name, quantity_name)] = item

        else:
            event.ignore()
    
    def remove_channel(self):
        # TODO: Handle quantity removal when a channel is removed
        selected_item = self.currentItem()
        if selected_item is not None:     
            instrument_name = selected_item.text(1)
            quantity_name = selected_item.text(0)       
            del self.quantities_added[(instrument_name, quantity_name)]
            self.takeTopLevelItem(self.indexOfTopLevelItem(selected_item))


    def log_channels_table_selection_changed(self):
        selected_item = self.currentItem()
        pass

    def get_log_table_quantities(self):
        output_quantities = self.quantities_added.keys()
        return list(output_quantities)