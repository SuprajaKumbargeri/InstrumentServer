import logging
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from GUI.quantity_frames import *
# from Instrument.instrument_manager import InstrumentManager

class ChannelsTreeWidget(QTreeWidget):
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        # dictionary for added channels in the table
        self.channels_added = dict()

        """
        Column Order:
        [Instrument, Name, Instr. value, Phys. value, Server]
        """
        self.setHeaderLabels(['Instrument', 'Name', 'Instr. value', 'Phys. value', 'Address'])
        
        # Allow only one selection at a time -> SingleSelection
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.itemSelectionChanged.connect(self.channels_table_selection_changed)
        self.itemDoubleClicked.connect(self.show_quantity_frame_gui)

    def add_channel_item(self, instrument_manager):
        im = instrument_manager
        if im.name not in self.channels_added:
            self.channels_added[im.name] = im
            parent = QTreeWidgetItem([im.name])
            for quantity in im.quantity_names:
                quantity_info = im.get_quantity_info(quantity)
                value = ""
                # set quantity value to last known value in DB or default value
                if quantity_info['latest_value']:
                    value = str(quantity_info['latest_value'])
                else:
                    value = str(quantity_info['def_value'])
                if quantity_info['unit']:
                    value += "" + quantity_info['unit']
                QTreeWidgetItem(parent, [quantity,'',value])
            
            self.addTopLevelItem(parent)
            parent.setExpanded(True)

    def remove_channel(self):
        # May be moved to the experimentGUI class' remove method along with changes to items on other tables
        selected_item = self.currentItem()
        if selected_item is not None:            
            if selected_item.childCount() > 0:
                # Selected item is a parent
                del self.channels_added[selected_item.text(0)]
                while selected_item.childCount() > 0:
                    selected_item.takeChild(0)
                self.takeTopLevelItem(self.indexOfTopLevelItem(selected_item))  

    def show_quantity_frame_gui(self, selected_item, column=None):   
        parent_item = selected_item.parent()
        if parent_item is not None:
            quantity = selected_item.text(0)
            cute_name = parent_item.text(0)
            im = self.channels_added[cute_name]
            quantity_info = im.get_quantity_info(quantity)
            print(quantity_info)

            frame = quantity_frame_factory(quantity_info, im.get_value, im.set_value,
                                            im.set_default_value, self._handle_quant_value_change, self.logger)
            
            dialog = ModifyQuantity(quantity_info, frame)
            print(dialog.exec())
            quantity_info = im.get_quantity_info(quantity)
            if quantity_info['latest_value']:
                value = str(quantity_info['latest_value'])
            else:
                value = str(quantity_info['def_value'])
            if quantity_info['unit']:
                value += "" + quantity_info['unit']
            selected_item.setText(2, value)


    def _handle_quant_value_change(self, state_quant_name, state_value):
        """Called by QuantityFrame when the quantity's value is changed.
        Sets visibility of other quantities depending on new value"""
        # TODO:
        # for quantity_frame in self.quantity_frames:
        #     # Not dependent on the quantity that changed
        #     if quantity_frame.state_quant != state_quant_name:
        #         continue

        #     if state_value in quantity_frame.state_values:
        #         quantity_frame.setHidden(False)
        #         self.logger.debug(f"{quantity_frame.name} is now visible.")
        #     # the list is populated with quantity.state_values in user form
        #     elif state_value in (self._im.convert_return_value(state_quant_name, v) for v in quantity_frame.state_values):
        #         quantity_frame.setHidden(False)
        #         self.logger.debug(f"{quantity_frame.name} is now visible.")
        #     else:
        #         quantity_frame.setHidden(True)
        #         self.logger.debug(f"{quantity_frame.name} is now hidden.")
        pass

    def channels_table_selection_changed(self):
        selected_item = self.currentItem()
        if selected_item is not None:
            if selected_item.childCount() == 0:
                # Selected item is a child
                # Not important
                pass

    def startDrag(self, supportedActions):
        items = self.selectedItems() # only a single item is configured to be selected at once
        if len(items) == 0:
            return
        parent = items[0].parent()
        if not parent:
            return
        drag = QDrag(self)
        mime_data = self.mimeData(items)
        drag.setMimeData(mime_data)
        drag.exec(supportedActions)
    

class AddChannelDialog(QDialog):
    def __init__(self, connected_ins: dict):
        super().__init__()
        
        self.setWindowTitle("Add Instrument")

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['Instrument', 'Name', 'Address'])
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        
        # Add the items to the tree widget
        for cute_name, ins in connected_ins.items():
            item = QTreeWidgetItem([cute_name]) # Also get address and instrument model name
            self.tree_widget.addTopLevelItem(item)
        
        # Add the tree widget to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, 
                                        self, 
                                        accepted=self.accept, 
                                        rejected=self.reject))
        self.setLayout(layout)

    def get_selected_item(self):
        selected_item = self.tree_widget.currentItem()
        if selected_item is not None:
            return selected_item.text(0)
        else:
            return None
        
class ModifyQuantity(QDialog):
    def __init__(self, quantity_info, frame):
        super().__init__()

        self.setWindowTitle(f"Edit {quantity_info['cute_name']}")
        button_section = QHBoxLayout()
        set_value_btn = QPushButton("Set default value")
        set_value_btn.clicked.connect(frame.set_default_value)
        button_section.addWidget(set_value_btn)

        get_value_btn = QPushButton("Query quantity value")
        get_value_btn.clicked.connect(frame.get_value)
        button_section.addWidget(get_value_btn)

        ok_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        ok_btn.accepted.connect(self.accept)
        button_section.addWidget(ok_btn)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(frame)
        dialog_layout.addLayout(button_section)
        self.setLayout(dialog_layout)
