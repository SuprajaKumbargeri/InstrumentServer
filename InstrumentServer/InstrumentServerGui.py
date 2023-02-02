import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


###################################################################################
# InstrumentServerWindow
###################################################################################

class InstrumentServerWindow(QMainWindow):

    def __init__(self):
        print('Initializing Instrument Server GUI...')
        super(InstrumentServerWindow, self).__init__()
        self.greenIcon = QIcon("./Icons/greenIcon.png")
        self.redIcon = QIcon("./Icons/redIcon.png")

        # The "top most" layout is vertical box layout (top -> bottom)
        self.main_layout = QVBoxLayout()

        # This is the outermost widget
        self.main_widget = QWidget()

        self.setWindowTitle("Instrument Server")
        self.construct_menu()

        self.construct_instrument_table_header()

        # Since we need multiple columns, we cannot use QListWidget. Instead, we can use QTreeWidget
        # since it support columns.
        self.instrument_tree = QTreeWidget(self)
        self.instrument_tree.setHeaderLabels(['Instrument Model', 'Cute Name', 'Interface', 'IP Address'])

        # Allow only one selection at a time -> SingleSelection
        self.instrument_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.instrument_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Some sample data (remove)
        self.add_instrument_to_list('33220A', 'Lab Instrument A', 'TCPIP0', '192.168.0.7')
        self.add_instrument_to_list('SG22000PRO', 'Lab Instrument B', 'ASRL3', '-')
        self.add_instrument_to_list('PS6000', 'Lab Instrument C', 'USB-CUSTOM', '-')

        self.instrument_tree.itemSelectionChanged.connect(self.instrument_selected_changed)
        self.main_layout.addWidget(self.instrument_tree)

        self.construct_bottom_buttons()
        self.construct_instrument_server_status()

        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)

        # Set the central widget
        self.setCentralWidget(self.main_widget)

        print('Done initializing Instrument Server GUI')

    def construct_menu(self):
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.exit_gui)

        menu = self.menuBar()
        menu.addSeparator()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(exit_action)

        help_menu = menu.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.about_action)
        help_menu.addAction(about_action)

    def construct_instrument_table_header(self):
        table_header = QWidget()
        table_header_layout = QHBoxLayout()

        instrument_status_lbl = QLabel("Laboratory Instruments:")
        table_header_layout.addWidget(instrument_status_lbl)
        table_header_layout.setAlignment(instrument_status_lbl, Qt.AlignmentFlag.AlignLeft)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_btn_clicked)
        table_header_layout.addWidget(connect_btn)

        connect_all_btn = QPushButton("Connect All")
        connect_all_btn.clicked.connect(self.connect_all_btn_clicked)
        table_header_layout.addWidget(connect_all_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_btn_clicked)
        table_header_layout.addWidget(close_btn)

        close_all_btn = QPushButton("Close All")
        close_all_btn.clicked.connect(self.connect_all_btn_clicked)
        table_header_layout.addWidget(close_all_btn)

        table_header.setLayout(table_header_layout)
        self.main_layout.addWidget(table_header)

    def construct_bottom_buttons(self):
        bottom_button_group_widget = QWidget()
        bottom_button_layout = QHBoxLayout()

        add_btn = QPushButton("Add")
        add_btn.setIcon(self.greenIcon)
        add_btn.clicked.connect(self.add_btn_clicked)
        bottom_button_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.setIcon(self.redIcon)
        remove_btn.clicked.connect(self.remove_btn_clicked)
        bottom_button_layout.addWidget(remove_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.settings_btn_clicked)
        bottom_button_layout.addWidget(settings_btn)

        close_btn = QPushButton("Exit")
        close_btn.clicked.connect(self.exit_gui)
        bottom_button_layout.addWidget(close_btn)

        bottom_button_group_widget.setLayout(bottom_button_layout)
        self.main_layout.addWidget(bottom_button_group_widget)

    def construct_instrument_server_status(self):
        status_widget = QWidget()
        status_layout = QHBoxLayout()

        instrument_server_status_lbl = QLabel("Instrument Server Is Running")
        status_layout.addWidget(instrument_server_status_lbl)
        status_layout.setAlignment(instrument_server_status_lbl, Qt.AlignmentFlag.AlignRight)

        status_widget.setLayout(status_layout)

        self.main_layout.addWidget(status_widget)

    # Defines exit behavior
    def exit_gui(self):
        print('Exit was clicked')
        self.confirm_shutdown()

    # Defines about behavior
    def about_action(self):
        msgBox = QMessageBox(self)
        msg = 'Instrument Server\nCSCI 5040 & CSCI 5050 Class Project\nVersion: 0.02'

        msgBox.setWindowTitle("About Instrument Server")
        msgBox.setText(msg)
        msgBox.exec()

    def instrument_selected_changed(self):
        selected_instruments = self.instrument_tree.selectedItems()

        if len(selected_instruments) > 0:
            log_instrument = 'Currently selected instrument: {} {}'.format(selected_instruments[0].text(0),
                                                                           selected_instruments[0].text(1))
            print(log_instrument)

    def settings_btn_clicked(self):
        print('Settings was clicked')

    def add_btn_clicked(self):
        print('Add was clicked')

    def remove_btn_clicked(self):
        print('Remove was clicked')

    def connect_btn_clicked(self):
        print('Connect was clicked')

    def connect_all_btn_clicked(self):
        print('Connect All was clicked')

    def close_btn_clicked(self):
        print('Close was clicked')

    def close_all_btn_clicked(self):
        print('Close All was clicked')

    def closeEvent(self, event):
        """Overrides closeEvent so that we throw a Dialogue question whether to exit or not."""
        button = QMessageBox.question(self, "Instrument Server",
                                      "Are you sure you want to exit? This will close all instruments.")

        if button == QMessageBox.StandardButton.No:
            # Ignore the event that brings down this window
            event.ignore()

    def confirm_shutdown(self):
        button = QMessageBox.question(self, "Instrument Server",
                                      "Are you sure you want to exit? This will close all instruments.")

        if button == QMessageBox.StandardButton.Yes:
           self.hide()

    def add_instrument_to_list(self, model: str, cute_name: str, interface: str, address: str):
        newItem = QTreeWidgetItem(self.instrument_tree, [model, cute_name, interface, address])
        newItem.setIcon(0, self.redIcon)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InstrumentServerWindow()
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(800, 600)
    mainWin.show()
    app.exec()
