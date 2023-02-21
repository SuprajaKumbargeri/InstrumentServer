import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from . import db
from . import instrument_connection_service as ics


###################################################################################
# InstrumentServerWindow
###################################################################################

class InstrumentServerWindow(QMainWindow):

    def __init__(self, flask_app):
        print('Initializing Instrument Server GUI...')

        # Convenience flag preventing VISA/DB aspects from being automatically called at startup
        self.dev_machine = False

        super(InstrumentServerWindow, self).__init__()

        self.currently_selected_instrument = None

        self.flask_app = flask_app

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
        self.instrument_tree.setHeaderLabels(['Instrument Model', 'Cute Name', 'Address'])

        # Allow only one selection at a time -> SingleSelection
        self.instrument_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.instrument_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        if not self.dev_machine:
            self.get_known_instruments()

        self.instrument_tree.itemSelectionChanged.connect(self.instrument_selected_changed)
        self.main_layout.addWidget(self.instrument_tree)

        self.construct_bottom_buttons()
        self.construct_instrument_server_status()

        # Set the layout for main widget
        self.main_widget.setLayout(self.main_layout)

        # Set the central widget
        self.setCentralWidget(self.main_widget)

        # Setup Experiment GUI
        from GUI.experimentWindowGui import ExperimentWindowGui
        self.experiment_window_gui = ExperimentWindowGui(self)

        print('Done initializing Instrument Server GUI')

    def construct_menu(self):
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.exit_gui)

        menu = self.menuBar()
        menu.addSeparator()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(exit_action)

        edit_menu = menu.addMenu("&Edit")

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

        create_experiment_btn = QPushButton("Create Experiment")
        create_experiment_btn.clicked.connect(self.create_experiment_clicked)
        status_layout.setAlignment(create_experiment_btn, Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(create_experiment_btn)

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
            self.currently_selected_instrument = selected_instruments[0].text(1)

    def settings_btn_clicked(self):
        print('Settings was clicked')

    def create_experiment_clicked(self):
        print('Create Experiment was clicked')
        self.show_experiment_window()

    def add_btn_clicked(self):
        print('Add was clicked')

    def remove_btn_clicked(self):
        print('Remove was clicked')

    def show_experiment_window(self):
        self.experiment_window_gui.show()

    def connect_btn_clicked(self):
        print('Connect was clicked')

        # Check if an intrument was selected
        if self.currently_selected_instrument:
            connect_result, fail_msg = ics.connect_to_visa_instrument(self.currently_selected_instrument)

            if connect_result:
                current_item = self.instrument_tree.currentItem()
                current_item.setIcon(0, self.greenIcon)
            else:
                QMessageBox.critical(self, 'ERROR', 'Could not connect to instrument: {} {}'
                                     .format(self.currently_selected_instrument, fail_msg))
        else:
            QMessageBox.warning(self, 'Warning', 'No Instrument was selected!')

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

    def add_instrument_to_list(self, model: str, cute_name: str, address: str) -> None:
        newItem = QTreeWidgetItem(self.instrument_tree, [model, cute_name, address])
        newItem.setIcon(0, self.redIcon)

    def clear_instrument_list(self):
        """
        Clears the Instrument List 
        """
        print('Clearing Instrument List...')
        self.instrument_tree.clear()

    def get_known_instruments(self):

        self.clear_instrument_list()
        connection = None

        with self.flask_app.app_context():
            try:
                connection = db.get_db()

                with connection.cursor() as cursor:
                    all_instruments_query = "SELECT * FROM {};".format("instruments")
                    cursor.execute(all_instruments_query)
                    result = cursor.fetchall()

                    for instrument in result:
                        cute_name = instrument[0]
                        manufacturer = instrument[1]
                        interface = instrument[2]
                        ip_address = instrument[3]
                        serial = instrument[4]
                        via = instrument[5]

                        print(ip_address)

                        # If an IP Address was provided, use it for Address column, otherwise use the Interface
                        self.add_instrument_to_list(manufacturer,
                                                    cute_name,
                                                    (ip_address if ip_address != None else interface))

            except Exception as ex:
                print('There was a problem getting all known instruments {}'.format(ex))

            finally:
                # Make sure we always close the connection
                db.close_db(connection)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InstrumentServerWindow()
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(800, 600)
    mainWin.show()
    app.exec()
