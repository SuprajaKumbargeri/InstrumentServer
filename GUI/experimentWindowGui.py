import logging
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from GUI.experiment_runner_gui import ExperimentRunner


###################################################################################
# ExperimentWindowGui
###################################################################################
class ExperimentWindowGui(QMainWindow):
    def __init__(self, parent_gui, logger: logging.Logger):
        super().__init__()
        self.parent_gui = parent_gui
        self.my_logger = logger
        self.setWindowTitle('Experiment')
        self.resize(1000, 800)

        lab_experiment_icon = QIcon("../Icons/labExperiment.png")
        self.setWindowIcon(lab_experiment_icon)

        # Experiment runner GUI
        self.experiment_runner_gui = ExperimentRunner(self, self.my_logger)

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
        self.construct_logging_section()

        # Set the central widget
        self.setCentralWidget(self.main_widget)

        # Make the Menu Bar
        self.construct_experiment_menu_bar()

    def get_logger(self):
        """Get the application logger"""
        return self.my_logger

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
        GUI Section on the right-top with step sequence
        """
        # The main widget in for this section
        self.right_side_section = QVBoxLayout()

        play_icon = QIcon("../Icons/playButton.png")
        experiment_runner_btn = QPushButton("Experiment Runner")
        experiment_runner_btn.setIcon(play_icon)
        experiment_runner_btn.clicked.connect(self.show_experiment_runner_window)

        self.right_side_section.addWidget(experiment_runner_btn)
        self.right_side_section.setAlignment(experiment_runner_btn, Qt.AlignmentFlag.AlignRight)

        # The main widget for step sequence section
        self.step_sequence_group = QGroupBox("Step sequence")

        # The main layout for this section
        step_sequence_main_layout = QVBoxLayout()

        # This is the table for looping values in the experiment
        step_sequence_table = QTreeWidget()

        # Disabling arrows in the Tree Widget
        step_sequence_table.setStyleSheet( "QTreeWidget::branch{border-image: url(none.png);}")

        # Tree Widget Items remain expanded, disabling the option to toggle expansion
        step_sequence_table.setItemsExpandable(False)

        # Allow only one selection at a time -> SingleSelection
        step_sequence_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        step_sequence_table.setHeaderLabels(['Channel', '# pts.', 'Step list', 'Output range'])
        header = step_sequence_table.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)        
       
        step_sequence_table.itemSelectionChanged.connect(self.step_sequence_table_selection_changed)

        """
        Column Order:
        ['Channel', '# pts.', 'Step list', 'Output range']
        """
        # TODO: Remove later (example data)
        first_loop_sequence = QTreeWidgetItem(step_sequence_table, ['gen - Frequency', '51', '5 GHz - 10 GHz', '5 GHz - 10 GHz'])
        second_loop_sequence = QTreeWidgetItem(first_loop_sequence, ['gen - Power', '51', '10 dBm - 20 dBm', '10 dBm - 20 dBm'])
        third_loop_sequence = QTreeWidgetItem(second_loop_sequence, ['gen - Phase', '180', '0 rad - 3.14 rad', '0 rad - 3.14 rad'])
        
        different_loop_sequence = QTreeWidgetItem(step_sequence_table, ['another_channel - Voltage', '100', '-5 V - 5 V', '-5 V - 5 V'])
        different_inner_loop_sequence = QTreeWidgetItem(different_loop_sequence, ['another_channel - Frequency', '10', '1 GHz - 10 GHz', '1 GHz - 10 GHz'])

        # Expand all the inner items
        step_sequence_table.expandAll()

        step_sequence_main_layout.addWidget(step_sequence_table)

        # Button section for 'edit' and 'remove' options
        button_section_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit...")
        button_section_layout.addStretch(1)
        button_section_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")        
        button_section_layout.addWidget(remove_btn)

        # Add button_section to the main layout
        step_sequence_main_layout.addLayout(button_section_layout)

        self.step_sequence_group.setLayout(step_sequence_main_layout)

        # Stretch factor for 'step sequence' is set to 3
        self.right_side_section.addWidget(self.step_sequence_group, 3)

    def construct_logging_section(self):
        """
        GUI Section on the right-bottom with log channels, comment and timing
        """
        #############################################
        # Log channels section
        #############################################

        # The main widget for log channels section
        self.log_channels_group = QGroupBox("Log channels")

        # The main layout for log channels section
        log_channels_group_main_layout = QVBoxLayout()

        # This is the table for output channels in the experiment
        log_channels_table = QTreeWidget()

        # Allow only one selection at a time -> SingleSelection
        log_channels_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Tree Widget Items remain expanded, disabling the option to toggle expansion
        log_channels_table.setItemsExpandable(False)

        log_channels_table.setHeaderLabels(['Channel', 'Instrument', 'Address'])
        header = log_channels_table.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  
       
        log_channels_table.itemSelectionChanged.connect(self.log_channels_table_selection_changed)

        """
        Column Order:
        ['Channel', 'Instrument', 'Address']
        """
        # TODO: Remove later (example data)
        QTreeWidgetItem(log_channels_table, ['Sij vs Frequency', 'Agilent VNA NIST', 'IP: 16'])        
        
        log_channels_group_main_layout.addWidget(log_channels_table)

        # Button section for 'edit' and 'remove' options
        button_section_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit...")
        button_section_layout.addStretch(1)
        button_section_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")                
        button_section_layout.addWidget(remove_btn)

        # Add button_section to the main layout
        log_channels_group_main_layout.addLayout(button_section_layout)

        self.log_channels_group.setLayout(log_channels_group_main_layout)
        
        #############################################
        # Comment section
        #############################################

        # The main widget for comment section
        self.comment_group = QGroupBox("Comment")

        # The main layout for comment section
        comment_box_layout = QVBoxLayout()

        comment_box = QTextEdit()
        comment_box.textChanged.connect(self.comment_text_changed)

        comment_box_layout.addWidget(comment_box)
        self.comment_group.setLayout(comment_box_layout)

        #############################################
        # Timing section
        #############################################

        # The main widget for timing section
        self.timing_group = QGroupBox("Timing")

        # The main layout for timing section
        timing_layout = QFormLayout()

        # Widgets in the timing form
        self.delay_time = QDoubleSpinBox()
        timing_layout.addRow(QLabel("Delay between step and measure [s]:"), self.delay_time)
        # TODO: Connect later
        # self.delay_time.valueChanged.connect(delay_time_changed)

        self.estimated_time = QSpinBox()
        timing_layout.addRow(QLabel("Estimated time per point [s]:"), self.estimated_time)
        # TODO: Connect later
        # self.estimated_time.valueChanged.connect(delay_estimated_time)

        # TODO: Connect later to set time needed value
        self.time_needed = "0:00:00" # replace with calculated time needed value      
        timing_layout.addRow(QLabel("Time needed:"), QLabel(self.time_needed))

        self.timing_group.setLayout(timing_layout)

        # Horizontal layout to add comment and timing sections
        comment_timing_HLayout = QHBoxLayout()
        comment_timing_HLayout.addWidget(self.comment_group)
        comment_timing_HLayout.addWidget(self.timing_group)

        # Stretch factor for 'log channels' is set to 2
        self.right_side_section.addWidget(self.log_channels_group, 2)
        # Stretch factor for 'comment' and 'timing' is set to 1      
        self.right_side_section.addLayout(comment_timing_HLayout, 1)
        
        self.main_layout.addLayout(self.right_side_section)

    def experiment_runner_clicked(self):
        self.get_logger().debug('Experiment Runner clicked')
        self.show_experiment_runner_window()


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

    def show_experiment_runner_window(self):
        self.experiment_runner_gui.show()

    def exit_experiment_gui(self):
        """
        Closes the experiment GUI
        """
        print('Exiting ExperimentWindowGui...')
        self.close()

    def channels_table_selection_changed(self):
        pass

    def step_sequence_table_selection_changed(self):
        pass

    def log_channels_table_selection_changed(self):
        pass

    def comment_text_changed(self):
        pass
