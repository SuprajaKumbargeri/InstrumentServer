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
            address = data_dict['address']

            # TODO: Remove
            if (instrument_name, quantity_name) in self.quantities_added.keys():
                event.ignore()
                return
            
            item = QTreeWidgetItem(self, [quantity_name, instrument_name, address])
            self.quantities_added[(instrument_name, quantity_name)] = item

        else:
            event.ignore()
    
    """ Removes a selected quantitiy from the Log Channels Table """
    def remove_quantity(self):
        selected_item = self.currentItem()
        if selected_item is not None:     
            instrument_name = selected_item.text(1)
            quantity_name = selected_item.text(0)       
            del self.quantities_added[(instrument_name, quantity_name)]
            self.takeTopLevelItem(self.indexOfTopLevelItem(selected_item))

    """ Removes all quantities related to a instrument from the Log Channels Table """
    def remove_channel(self, cute_name):
        if cute_name:
            # Traverse the tree in reverse to remove the tree widgets that belong to an instrument
            for index in range(self.topLevelItemCount() -1, -1, -1):
                tree_item = self.topLevelItem(index)
                ins, qty = tree_item.text(1), tree_item.text(0)
                if (ins, qty) in self.quantities_added.keys() and ins == cute_name:
                    del self.quantities_added[(ins, qty)]
                    self.takeTopLevelItem(index)


    def log_channels_table_selection_changed(self):
        selected_item = self.currentItem()
        pass