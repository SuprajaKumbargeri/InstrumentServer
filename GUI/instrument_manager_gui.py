from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea)
from Insrument.instrument_manager import InstrumentManager
from GUI.quantity_frames import *

class InstrumentManagerGUI(QWidget):
    def __init__(self, instrument_manager: InstrumentManager):
        super(InstrumentManagerGUI, self).__init__()

        self._im = instrument_manager
        self.quantity_frames = list()
        self.section_frames = dict()

        self.scroll_layout = QVBoxLayout()

        # add all quantities to layouts dependent on section and group name
        self._build_quanitity_sections()
        # add sections to layout
        for section_name, section in self.section_frames.items():
            section.setHidden(True)
            self.scroll_layout.addWidget(section)
        self.scroll_layout.addStretch(1)

        self.section_frames['Modulation'].setHidden(False)

        # this widget is needed for the QScrollArea
        widget = QWidget()
        widget.setLayout(self.scroll_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(widget)
        self.scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self.setWindowTitle(f"{self._im.name} Manager")
        self.show()
        self.resize(800, 600)

    def _build_quanitity_sections(self):
        """Loops through all quantities and adds them to the correct groups and lookup list.
        Groups are then assigned to sections. Groups/sections can be found in instrument driver"""
        sections = dict()

        for quantity in self._im.quantity_names:
            quantity_info = self._im.get_quantity_info(quantity)

            frame = quantity_frame_factory(quantity_info, self._im.set_value,
                                           self._im.get_value, self.handle_combo_change)
            frame.setFixedHeight(40)

            # store all frames in a lookup list
            # This is used to hide quantities if their visibility is tied to another quantity value
            self.quantity_frames.append(frame)

            # get section name, default to Uncategorized
            section_name = quantity_info['section']
            if not section_name:
                section_name = 'Uncategorized'
            # get group name, default to Uncategorized
            group_name = quantity_info['groupname']
            if not group_name:
                group_name = 'Uncategorized'

            # create new section
            if section_name not in sections:
                sections[section_name] = dict()

            # add new frame to existing group
            if group_name in sections[section_name]:
                sections[section_name][group_name].append(frame)
            # create new group
            else:
                sections[section_name][group_name] = list()
                sections[section_name][group_name].append(frame)

        # construct frames for each section
        for section_name, section in sections.items():
            section_frame = QtW.QFrame()
            section_layout = QtW.QVBoxLayout()

            # construct groupboxes for each group
            for group_name in sections[section_name]:
                quantities = section[group_name]
                section_layout.addWidget(QuantityGroupBox(group_name, quantities))

            # set section layout and add to lookup dictionary
            section_frame.setLayout(section_layout)
            self.section_frames[section_name] = section_frame


    def handle_combo_change(self, quantity_name, state_value):
        """Called by ComboFrame when the combo's value is changed.
        Sets visibility of other quantities depending on new value"""
        for quantity_frame in self.quantity_frames:
            if quantity_frame.state_quant != quantity_name:
                continue

            if state_value in quantity_frame.state_values:
                quantity_frame.setHidden(False)
            else:
                quantity_frame.setHidden(True)

