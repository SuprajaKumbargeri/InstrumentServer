import logging
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from GUI.experiment_runner_gui import ExperimentRunner

from GUI.quantity_frames import *
from GUI.channels_table import *
from GUI.sequence_table import *
from GUI.log_channels_table import *

###################################################################################
# ExperimentWindowGui
###################################################################################
class ExperimentWindowGui(QMainWindow):
    def __init__(self, parent_gui, ics, logger: logging.Logger):
        super().__init__()
        self.parent_gui = parent_gui
        self.my_logger = logger
        self.setWindowTitle('Experiment')
        self.resize(1000, 800)
        self._ics = ics
        self._working_instruments = dict()

        # TODO: Move this to a DTO class
        self.input_DTO = None
        self.sequence_DTO = None
        self.output_DTO = None
        self.quantities_DTO = None

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
    
    def get_instrument_manager(self, cute_name):
        """Get the instrument manager object from instrument connection service"""
        return self._ics.get_instrument_manager(cute_name)

    ####################################################################
    # Channel table related implementation
    ####################################################################
    def construct_channels_section(self):
        """
        GUI Section on the left
        """
        # The main widget in this section
        self.channels_group = QGroupBox('Channels')

        # Set the layout for main widget    
        channels_section_main_layout = QVBoxLayout()

        self.channels_table = ChannelsTreeWidget(self._working_instruments, self.my_logger)

        # Placeholder - to be removed
        root_example = QTreeWidgetItem(self.channels_table, ['Rhode&Schwarz SG100', 'gen', '','', 'localhost'])
        QTreeWidgetItem(root_example, ['Frequency', '', '5 Ghz'])
        QTreeWidgetItem(root_example, ['Power', '', '-20 dBm'])
        QTreeWidgetItem(root_example, ['Phase', '', '0 rad'])
        QTreeWidgetItem(root_example, ['Mode', '', 'Normal'])
        QTreeWidgetItem(root_example, ['Output', '', 'Off'])
        root_example.setExpanded(True)
        channels_section_main_layout.addWidget(self.channels_table)

        # The section on the bottom that has buttons
        button_section_layout = QHBoxLayout()

        show_cfg_btn = QPushButton("Show cfg...")
        button_section_layout.addWidget(show_cfg_btn)
        button_section_layout.setAlignment(show_cfg_btn, Qt.AlignmentFlag.AlignLeft)

        add_btn = QPushButton("Add...")
        button_section_layout.addWidget(add_btn)
        add_btn.clicked.connect(self.add_channel)

        edit_btn = QPushButton("Edit...")
        button_section_layout.addWidget(edit_btn)
        edit_btn.clicked.connect(self.edit_channel_quantity)

        remove_btn = QPushButton("Remove")
        button_section_layout.addWidget(remove_btn)
        remove_btn.clicked.connect(self.remove_channel)
        button_section_layout.setAlignment(remove_btn, Qt.AlignmentFlag.AlignRight)

        # Add button_section to the main layout
        channels_section_main_layout.addLayout(button_section_layout)

        self.channels_group.setLayout(channels_section_main_layout)
        self.main_layout.addWidget(self.channels_group)

    def add_channel(self):
        """
        Implements the add instrument functionality to the Channel table
        """
        dialog = AddChannelDialog(self._ics._connected_instruments)
        if dialog.exec():
            # Get the selected item from the dialog box
            selected_item = dialog.get_selected_item()
            if selected_item is not None:
                instrument_manager = self.get_instrument_manager(selected_item)
                self.channels_table.add_channel_item(instrument_manager)

    def remove_channel(self):
        """
        Removes an added instrument from channel table
        """
        self.channels_table.remove_channel()
        # TODO: handle deletion from other tables
        return

    def edit_channel_quantity(self):
        """
        Modifies an existing instrument's quantity
        """
        if self.channels_table.currentItem() is not None:
            self.channels_table.show_quantity_frame_gui(self.channels_table.currentItem())
        return

    ####################################################################
    # Step sequence table related implementation
    ####################################################################
    def construct_step_sequence_section(self):
        """
        GUI Section on the right-top with step sequence
        """
        # The main widget in for this section
        self.right_side_section = QVBoxLayout()

        play_icon = QIcon("../Icons/playButton.png")
        experiment_runner_btn = QPushButton("Experiment Runner")
        experiment_runner_btn.setIcon(play_icon)
        experiment_runner_btn.clicked.connect(self.experiment_runner_clicked)

        self.right_side_section.addWidget(experiment_runner_btn)
        self.right_side_section.setAlignment(experiment_runner_btn, Qt.AlignmentFlag.AlignRight)

        # The main widget for step sequence section
        self.step_sequence_group = QGroupBox("Step sequence")

        # The main layout for this section
        step_sequence_main_layout = QVBoxLayout()

        # This is the table for looping values in the experiment
        self.step_sequence_table = StepSequenceTreeWidget(self._working_instruments, self.item_valid, self.my_logger)

        # Expand all the inner items
        self.step_sequence_table.expandAll() # TODO: Remove

        step_sequence_main_layout.addWidget(self.step_sequence_table)

        # Button section for 'edit' and 'remove' options
        button_section_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit...")
        button_section_layout.addStretch(1)
        button_section_layout.addWidget(edit_btn)
        edit_btn.clicked.connect(self.edit_quantity_sequence)

        remove_btn = QPushButton("Remove")        
        button_section_layout.addWidget(remove_btn)
        remove_btn.clicked.connect(self.remove_quantity_sequence)

        # Add button_section to the main layout
        step_sequence_main_layout.addLayout(button_section_layout)

        self.step_sequence_group.setLayout(step_sequence_main_layout)

        # Stretch factor for 'step sequence' is set to 3
        self.right_side_section.addWidget(self.step_sequence_group, 3)

    def edit_quantity_sequence(self):
        """
        Modifies an existing sequence for a quantity
        """
        if self.step_sequence_table.currentItem() is not None:
            self.step_sequence_table.show_sequence_constructor_gui(self.step_sequence_table.currentItem())
        return
    
    def remove_quantity_sequence(self):
        """
        Removes an added quantity from sequence table
        """
        self.step_sequence_table.remove_channel()
        return

    ####################################################################
    # Implementation related to logging, comments and timing
    ####################################################################
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
        self.log_channels_table = LogChannelsTreeWidget(self._working_instruments, self.item_valid, self.my_logger)

        log_channels_group_main_layout.addWidget(self.log_channels_table)        

        # Button section for 'edit' and 'remove' options
        button_section_layout = QHBoxLayout()
        '''
        edit_btn = QPushButton("Edit...")
        button_section_layout.addStretch(1)
        button_section_layout.addWidget(edit_btn)
       '''
        
        remove_btn = QPushButton("Remove")
        button_section_layout.addStretch(1)                
        button_section_layout.addWidget(remove_btn)
        remove_btn.clicked.connect(self.remove_log_quantity)

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

    def remove_log_quantity(self):
        """
        Removes an added quantity from log table
        """
        self.log_channels_table.remove_channel()
        return

    def comment_text_changed(self):
        pass


    ####################################################################
    # Experiment Runner related implementation
    ####################################################################
    def experiment_runner_clicked(self):
        self.get_logger().debug('Experiment Runner clicked')
        if self.validate_experiment_data():
            self.construct_DTO()
            self.show_experiment_runner_window()
        else:
            return


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


    ####################################################################
    # Data validation related implementaion
    ####################################################################
    def item_valid(self, ins_name: str, qty_name: str):
        if self.step_sequence_table.check_item_valid(ins_name, qty_name) and self.log_channels_table.check_item_valid(ins_name, qty_name):
            return True
        else:
            return False
        
    def validate_experiment_data(self):

        # Ensure no over-lap between step sequence table and log channels table quantities
        if set(self.step_sequence_table.quantities) & (set(self.log_channels_table.quantities)):
            self.get_logger().error("Duplicate quantities in Step Sequence and Log Channels tables.")
            return False

        # Ensure sequences at the same level have the same number of points
        if not self.step_sequence_table.validate_sequence():
            return False
        
        return True       
        

    def construct_DTO(self):
        self.get_logger().info("Constructing DTO ...")
        input, sequence = self.step_sequence_table.get_step_sequence_quantities()
        output = self.log_channels_table.get_log_table_quantities()

        # dictionary of quantity manager objects involved in the experiment
        # key: (instrument_name, quantity_name)
        # value: QuantityManager object
        quantities = {}
        # add all input quantities
        for (ins, qty) in input:
            quantities[(ins, qty)] = self._working_instruments[ins].quantities[qty]
        for (ins, qty) in output:
            quantities[(ins, qty)] = self._working_instruments[ins].quantities[qty]
        
        # TODO: Construct a DTO class object
        self.input_DTO = input
        self.sequence_DTO = sequence
        self.output_DTO = output
        self.quantities_DTO = quantities
        return


