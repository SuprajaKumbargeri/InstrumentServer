import logging
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from GUI.quantity_frames import *
import json
# from Instrument.instrument_manager import InstrumentManager

class ChannelsTreeWidget(QTreeWidget):
    def __init__(self, parent_gui, channels_added: dict(), logger: logging.Logger):
        super().__init__()

        self._parent_gui = parent_gui
        self.logger = logger
        # dictionary for added channels in the table
        self.channels_added = channels_added
        # dictionary for quantities of each added channel
        # TODO: change dictionary layout to (ins, qty): quantity
        self.quantities_added = dict()

        """
        Column Order:
        [Instrument, Name, Quantitiy Value, Server]
        """
        self.setHeaderLabels(['Instrument', 'Name', 'Value', 'Address'])

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
        cute_name = im.name
        model = im.model_name
        address = im.address
        if cute_name not in self.channels_added:
            self.channels_added[cute_name] = im
            self.quantities_added[cute_name] = {}
            self.parent = QTreeWidgetItem([cute_name, model, '', address])
            for quantity in im.quantities.values():
                quantity_name = quantity.name
                value = self.get_value(quantity)
                unit = ''

                # Handle this in Quantity Manager -> convert_return_value()
                if value and quantity.data_type.upper() == 'DOUBLE':
                    value = float(value)
                
                if quantity.unit and value:
                    unit = quantity.unit
                quantity_widget = QTreeWidgetItem(self.parent, [quantity_name,'', str(value) + unit])
                self.quantities_added[cute_name][quantity_name] = quantity_widget

                quantity_widget.setHidden(quantity.is_visible)

            self.addTopLevelItem(self.parent)
            self.parent.setExpanded(True)

    def get_value(self, quantity):
        try:
            value = quantity.get_value()
            self._handle_quant_value_change(quantity.name, value)
            return value
        except Exception as e:
            self.logger.error(f"Error querying '{quantity.name}': {e}")
            QtW.QMessageBox.critical(self, f"Error querying '{quantity.name}'", str(e))

    def handle_incoming_value(self, value):
        """Handles any value returned by instrument to be properly displayed. Should be implemented by child class"""
        pass
        # raise NotImplementedError()

    def remove_channel(self):
        selected_item = self.currentItem()
        if selected_item is not None:            
            if selected_item.childCount() > 0:
                cute_name = selected_item.text(0)
                # Selected item is a parent
                del self.channels_added[selected_item.text(0)]
                while selected_item.childCount() > 0:
                    selected_item.takeChild(0)
                self.takeTopLevelItem(self.indexOfTopLevelItem(selected_item))
                return cute_name
        return
    
    def show_quantity_frame_gui(self, selected_item, column=None):   
        parent_item = selected_item.parent()
        if parent_item is not None:
            quantity_name = selected_item.text(0)
            cute_name = parent_item.text(0)
            im = self.channels_added[cute_name]
            quantity = im.quantities[quantity_name]
            
            frame = quantity_frame_factory(quantity, self._handle_quant_value_change, self.logger)
            dialog = ModifyQuantity(quantity, frame)
            dialog.exec()

            value = self.get_value(quantity)
            unit = ''

            # Handle this in Quantity Manager -> convert_return_value()
            if value and quantity.data_type.upper() == 'DOUBLE':
                value = float(value)
            
            if quantity.unit and value:
                unit = quantity.unit

            selected_item.setText(2, str(value) + unit)
    
    def _handle_quant_value_change(self, quantity_changed, new_value):
        """Called by QuantityFrame when the quantity's value is changed.
        Sets visibility of other quantities depending on new value"""
        if self.currentItem():
            selected_item = self.currentItem()
            cute_name = selected_item.parent().text(0)
        else:
            cute_name = self.parent.text(0)
        _im = self.channels_added[cute_name]
        _im.update_visibility(quantity_changed, new_value)
        quantity_widgets = self.quantities_added[cute_name]

        for quantity_name, quantity in _im.quantities.items():
            if quantity_name in quantity_widgets.keys():
                quantity_widget = quantity_widgets[quantity_name]
                quantity_widget.setHidden(not quantity.is_visible)

            # Remove all quantities related to this instrument from the Step Sequence and Log Channels tables after a value change in the Channels Table
            # This is to avoid having non-visible quantities being present in the Step Sequence and Log Channels table
            self._parent_gui.remove_experiment_quantities(cute_name)


    def channels_table_selection_changed(self):
        selected_item = self.currentItem()
        if selected_item is not None:
            if selected_item.childCount() == 0:
                # Selected item is a child
                # Not important
                pass

    def startDrag(self, supportedActions):
        selected_item = self.currentItem() # only a single item is configured to be selected at once
        parent_item = selected_item.parent()
        if not parent_item:
            return
        data_dict = {'instrument_name': parent_item.text(0), 'quantity_name': selected_item.text(0), 'address': parent_item.text(3)}

        # Serialize the dictionary as JSON
        mime_data = QMimeData()
        mime_data.setData('application/json', json.dumps(data_dict).encode())
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(supportedActions)


class AddChannelDialog(QDialog):
    def __init__(self, connected_ins: dict):
        super().__init__()

        self.setWindowTitle("Add Instrument")
        lab_experiment_icon = QIcon("../Icons/labExperiment.png")
        self.setWindowIcon(lab_experiment_icon)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['Instrument', 'Name', 'Address'])
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

        # Add the items to the tree widget
        for cute_name, ins in connected_ins.items():
            item = QTreeWidgetItem([cute_name, ins.model_name, ins.address])
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
    def __init__(self, quantity, frame):
        super().__init__()

        self.setWindowTitle(f"Edit {quantity.name}")
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