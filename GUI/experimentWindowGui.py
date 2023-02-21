from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from InstrumentServer.InstrumentServerGui import InstrumentServerWindow


###################################################################################
# ExperimentWindowGui
###################################################################################
class ExperimentWindowGui(QMainWindow):
    def __init__(self, parent_gui: InstrumentServerWindow):
        super().__init__()
        self.parent_gui = parent_gui
        self.setWindowTitle('Experiment')
        self.resize(1000, 800)

        # This is the outermost widget or the "main" widget
        self.main_widget = QWidget()

        # The "top most" layout is vertical box layout (top -> bottom)
        self.main_layout = QHBoxLayout()

        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)

        # Make the left GUI section
        self.construct_channels_section()

        # Make the right GUI section
        self.construct_step_sequence_section()

        # Set the central widget
        self.setCentralWidget(self.main_widget)

        # Make the Menu Bar
        self.construct_experiment_menu_bar()

    def construct_channels_section(self):
        """
        GUI Section on the left
        """
        # The main widget in this section
        self.channels_group = QGroupBox('Channels')

        # Set the layout for main widget    
        channels_section_main_layout = QVBoxLayout()

        # This is that table full of instruments and their values
        channels_table = QTreeWidget()
        channels_table.setHeaderLabels(['Instrument', 'Name/Address', 'Instr. value', 'Phys. value', 'Server'])

        # Allow only one selection at a time -> SingleSelection
        channels_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = channels_table.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        channels_table.itemSelectionChanged.connect(self.channels_table_selection_changed)

        """
        Column Order:
        [Instrument, Name/Address, Instr. value, Phys. value, Server]
        """
        # TODO: Remove later (example data)
        root_example = QTreeWidgetItem(channels_table, ['Rhode&Schwarz SG100', 'gen', '','', 'localhost'])
        QTreeWidgetItem(root_example, ['Frequency', '', '5 Ghz'])
        QTreeWidgetItem(root_example, ['Power', '', '-20 dBm'])
        QTreeWidgetItem(root_example, ['Phase', '', '0 rad'])
        QTreeWidgetItem(root_example, ['Mode', '', 'Normal'])
        QTreeWidgetItem(root_example, ['Output', '', 'Off'])
        root_example.setExpanded(True)
        channels_section_main_layout.addWidget(channels_table)

        #############################################
        # The section on the bottom that has buttons
        #############################################
        button_section_layout = QHBoxLayout()

        show_cfg_btn = QPushButton("Show cfg...")
        button_section_layout.addWidget(show_cfg_btn)
        button_section_layout.setAlignment(show_cfg_btn, Qt.AlignmentFlag.AlignLeft)

        set_value_btn = QPushButton("Set value...")
        button_section_layout.addWidget(set_value_btn)

        get_value_btn = QPushButton("Get value")
        button_section_layout.addWidget(get_value_btn)

        add_btn = QPushButton("Add...")
        button_section_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit...")
        button_section_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")
        button_section_layout.addWidget(remove_btn)
        button_section_layout.setAlignment(remove_btn, Qt.AlignmentFlag.AlignRight)

        # Add button_section to the main layout
        channels_section_main_layout.addLayout(button_section_layout)

        self.channels_group.setLayout(channels_section_main_layout)
        self.main_layout.addWidget(self.channels_group)

    def construct_step_sequence_section(self):
        """
        GUI Section on the right
        """
        # The main widget in for this section
        self.step_sequence_group = QGroupBox("Step sequence")

        # The main layout for this section
        step_sequence_main_layout = QVBoxLayout()

        sample_placeholder_lbl = QLabel("This will be the Step Sequence section")
        step_sequence_main_layout.addWidget(sample_placeholder_lbl)

        self.step_sequence_group.setLayout(step_sequence_main_layout)
        self.main_layout.addWidget(self.step_sequence_group)


    def construct_experiment_menu_bar(self):
        """
        Constructs the Menu Bar on top
        """
        experiment_menu_bar = self.menuBar()
        experiment_menu_bar.addSeparator()
        file_menu = experiment_menu_bar.addMenu("&File")

        # Defines the action to exit GUI via the menu bar File section
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.exit_experiment_gui)
        file_menu.addAction(exit_action)

        edit_menu = experiment_menu_bar.addMenu("&Edit")
        help_menu = experiment_menu_bar.addMenu("&Help")

    def exit_experiment_gui(self):
        """
        Closes the experiment GUI
        """
        print('Exiting ExperimentWindowGui...')
        self.close()

    def channels_table_selection_changed(self):
        pass
