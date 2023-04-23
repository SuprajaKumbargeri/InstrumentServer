import sys
import requests

from PyQt6 import QtCore
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QFrame, QApplication, QMessageBox)
import logging

from DB import db
from GUI.setting_frames import StringSettingFrame, ComboBoxSettingFrame, FileDialogSettingFrame, SettingsGroupBox, \
    SettingFrameDTO, TwoRadioButtonSettingFrame, IntegerSettingFrame, SettingFrame

INTERFACES = ['TCPIP', 'USB', 'GPIB']
TERM_CHARS = ['Auto', 'None', 'CR', 'LF', 'CR+LF']


###################################################################################
# InstrumentSettingsGUI
###################################################################################
class InstrumentSettingsGUI(QWidget):
    def __init__(self, flask_app, parent_gui, logger, cute_name):
        super(InstrumentSettingsGUI, self).__init__()

        self.flask_app = flask_app
        self.parent_gui = parent_gui
        self.logger = logger
        self.cute_name = cute_name

        # Contains all the setting relevant to this instrument
        self.instrument_settings_dict = self._get_settings_for_instrument(self.cute_name)

        print(self.instrument_settings_dict)

        self.section_frames = dict()
        self.section_tree_weight = 1
        self.section_data_weight = 4

        self.scroll_layout = QVBoxLayout()

        self.scroll_layout.addStretch(1)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # this widget is needed for the QScrollArea
        widget = QWidget()
        widget.setLayout(self.scroll_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(widget)
        self.scroll_area.setWidgetResizable(True)

        # Build all the setting frames
        self.all_setting_frames = self._build_setting_sections()
        self._build_section_tree(self.all_setting_frames.keys())

        self._main_settings_frames = self.all_setting_frames['Main Settings']
        self._general_settings_frames = self.all_setting_frames['General Settings']
        self._visa_settings_frames = self.all_setting_frames['VISA Settings']

        # Populate just the Main Settings for now (init)
        self.main_settings_box = SettingsGroupBox('Main Settings', self._main_settings_frames)
        self.general_settings_box = SettingsGroupBox('General Settings', self._general_settings_frames)
        self.visa_settings_box = SettingsGroupBox('VISA Settings', self._visa_settings_frames)
        self.general_settings_box.setVisible(False)
        self.visa_settings_box.setVisible(False)

        self.scroll_layout.addWidget(self.main_settings_box)
        self.scroll_layout.addWidget(self.general_settings_box)
        self.scroll_layout.addWidget(self.visa_settings_box)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.section_tree, self.section_tree_weight)
        main_layout.addWidget(self.scroll_area, self.section_data_weight)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.full_layout = QVBoxLayout()
        self.full_layout.addWidget(main_widget)

        self._build_bottom_btn_section()
        self.setLayout(self.full_layout)

        self.section_tree.setCurrentItem(self.section_tree.topLevelItem(0))

        self.setWindowTitle("Instrument Settings")
        self.resize(800, 400)
        self.show()

    def _build_section_tree(self, setting_keys):
        self.section_tree = QTreeWidget(self)
        self.section_tree.setHeaderLabels(['Instrument Settings'])
        self.section_tree.itemSelectionChanged.connect(self._handle_section_change)

        # The sections remain static
        for section_name in setting_keys:
            QTreeWidgetItem(self.section_tree, [section_name])

    def _handle_section_change(self):
        selected_section_name = self.section_tree.currentItem().text(0)
        print(f'Selected {selected_section_name}')

        self.general_settings_box.setVisible(False)
        self.main_settings_box.setVisible(False)
        self.visa_settings_box.setVisible(False)

        match selected_section_name:
            case 'Main Settings':
                self.main_settings_box.setVisible(True)
            case 'General Settings':
                self.general_settings_box.setVisible(True)
            case 'VISA Settings':
                self.visa_settings_box.setVisible(True)

    def _build_bottom_btn_section(self):
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_data_clicked)

        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._update_settings_clicked)

        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self._exit_gui)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(quit_btn)

        self.full_layout.addLayout(button_layout)

    def _get_settings_for_instrument(self, cute_name):
        try:
            url = r'http://127.0.0.1:5000/instrumentDB/getInstrumentSettings'
            response = requests.get(url, params={'cute_name': cute_name})
            return dict(response.json())

        except Exception as ex:
            QMessageBox.critical(self, 'ERROR', f'Could not retrieve settings for instrument {self.cute_name}: {ex}')
            return {}

    def _build_setting_sections(self):
        setting_frames = dict()
        setting_frames['Main Settings'] = self._build_main_settings_frames()
        setting_frames['General Settings'] = self._build_general_settings_frames()
        setting_frames['VISA Settings'] = self._build_visa_settings_frames()

        return setting_frames

    def _build_main_settings_frames(self):
        """
        (Table is actually called instruments)
        "instrument_interface":
        {
            "address":
            "cute_name":
            "interface":
            "manufacturer":
            "serial":
            "visa":
        }
        """

        main_settings_frames = []

        instrument_interface_dict = self.instrument_settings_dict['instrument_interface']
        general_settings_dict = self.instrument_settings_dict['general_settings']

        unique_name_dto = SettingFrameDTO('Unique Name',
                                          instrument_interface_dict['cute_name'],
                                          'instruments',
                                          'cute_name',
                                          'cute_name',
                                          self.cute_name)

        unique_name_dto.cascade_update = True
        main_settings_frames.append(StringSettingFrame(unique_name_dto, self.logger))

        address_dto = SettingFrameDTO('Address',
                                      instrument_interface_dict['address'],
                                      'instruments',
                                      'address',
                                      'cute_name',
                                      self.cute_name)
        main_settings_frames.append(StringSettingFrame(address_dto, self.logger))

        interface_dto = SettingFrameDTO('Interface',
                                        instrument_interface_dict['interface'],
                                        'instruments',
                                        'interface',
                                        'cute_name',
                                        self.cute_name)
        main_settings_frames.append(ComboBoxSettingFrame(interface_dto, INTERFACES, self.logger))

        driver_path_dto = SettingFrameDTO('Driver Path',
                                          general_settings_dict['ini_path'],
                                          'general_settings',
                                          'ini_path',
                                          'cute_name',
                                          self.cute_name)
        main_settings_frames.append(FileDialogSettingFrame(driver_path_dto, self.logger))

        is_serial_dto = SettingFrameDTO('Serial Instrument',
                                        instrument_interface_dict['serial'],
                                        'instruments',
                                        'serial',
                                        'cute_name',
                                        self.cute_name)

        main_settings_frames.append(TwoRadioButtonSettingFrame(is_serial_dto, self.logger))

        is_visa_dto = SettingFrameDTO('VISA Instrument',
                                      instrument_interface_dict['visa'],
                                      'instruments',
                                      'visa',
                                      'cute_name',
                                      self.cute_name)

        main_settings_frames.append(TwoRadioButtonSettingFrame(is_visa_dto, self.logger))

        return main_settings_frames

    def _build_general_settings_frames(self):
        general_settings_frames = []
        general_settings_dict = self.instrument_settings_dict['general_settings']

        for column in list(general_settings_dict.keys()):
            # Skip this column
            if column == 'cute_name':
                continue

            frame_dto = SettingFrameDTO(str(column).upper(),
                                        general_settings_dict[column],
                                        'general_settings',
                                        column,
                                        'cute_name',
                                        self.cute_name)

            match column:
                case 'interface':
                    general_settings_frames.append(ComboBoxSettingFrame(frame_dto, INTERFACES, self.logger))

                case 'ini_path':
                    general_settings_frames.append(FileDialogSettingFrame(frame_dto, self.logger))

                case 'address':
                    frame_dto.label = 'Address (Pre-defined)'
                    general_settings_frames.append(StringSettingFrame(frame_dto, self.logger))

                case _:
                    general_settings_frames.append(StringSettingFrame(frame_dto, self.logger))

        return general_settings_frames

    def _build_visa_settings_frames(self):
        visa_settings_frames = []
        visa_settings_dict = self.instrument_settings_dict['visa']

        for column in list(visa_settings_dict.keys()):
            # Skip this column
            if column == 'cute_name':
                continue

            frame_dto = SettingFrameDTO(str(column).upper(),
                                        visa_settings_dict[column],
                                        'visa',
                                        column,
                                        'cute_name',
                                        self.cute_name)

            match column:
                case 'always_read_after_write' | 'gpib_go_to_local' | 'query_instr_errors' | 'reset' | 'tcpip_specify_port' | 'use_visa':
                    visa_settings_frames.append(TwoRadioButtonSettingFrame(frame_dto, self.logger))

                case 'baud_rate':
                    visa_settings_frames.append(IntegerSettingFrame(frame_dto, 110, 256000, self.logger))

                case 'data_bits':
                    visa_settings_frames.append(IntegerSettingFrame(frame_dto, 5, 8, self.logger))

                case 'error_bit_mask':
                    visa_settings_frames.append(IntegerSettingFrame(frame_dto, 0, 255, self.logger))

                case 'timeout':
                    frame_dto.label = 'Timeout (sec)'
                    visa_settings_frames.append(IntegerSettingFrame(frame_dto, 0, 3600, self.logger))

                case 'ini_path':
                    visa_settings_frames.append(FileDialogSettingFrame(frame_dto, self.logger))

                case 'term_char':
                    frame_dto.label = 'Termination Character(s)'
                    visa_settings_frames.append(ComboBoxSettingFrame(frame_dto, TERM_CHARS, self.logger))

                case 'tcpip_port':
                    frame_dto.label = 'TCP/IP Port'
                    visa_settings_frames.append(IntegerSettingFrame(frame_dto, 0, 65535, self.logger))

                case _:
                    visa_settings_frames.append(StringSettingFrame(frame_dto, self.logger))

        return visa_settings_frames

    def _construct_individual_frame_dict(self, label, value):
        return {'label': label, 'value': value}

    def _reset_data_clicked(self):
        self.logger.info('Reset was clicked')
        button = QMessageBox.question(self, "Reset View", 'Are you sure you want to restore original values?')

        if button == QMessageBox.StandardButton.Yes:
            self.main_settings_box.rest_all_my_frames()
            self.general_settings_box.rest_all_my_frames()
            self.visa_settings_box.rest_all_my_frames()

    def process_setting_updates(self, setting_dict, setting_frames):
        for frame in setting_frames:
            for entry in setting_dict.keys():
                if frame.get_frame_dto().db_column == entry:
                    if frame.get_gui_value() != setting_dict[entry]:
                        print(f'Frame: {frame.get_gui_value()} != {setting_dict[entry]}')
                        self._update_db_value_with_frame_data(frame)

    def _update_settings_clicked(self):
        self.logger.info('Update was clicked')

        error_occurred = False
        try:
            # Process Main Settings updates
            main_settings_dict = self.instrument_settings_dict['instrument_interface']
            self.process_setting_updates(main_settings_dict, self._main_settings_frames)

            # Process General Settings updates
            gen_settings_dict = self.instrument_settings_dict['general_settings']
            self.process_setting_updates(gen_settings_dict, self._general_settings_frames)

            # Process VISA Settings updates
            visa_settings_dict = self.instrument_settings_dict['visa']
            self.process_setting_updates(visa_settings_dict, self._visa_settings_frames)

        except Exception as ex:
            error_occurred = True
            QMessageBox.critical(self, 'ERROR', str(ex))

        if not error_occurred:
            msg_box = QMessageBox(self)
            msg = f'Instrument: ({self.cute_name}) was successfully updated.'
            msg_box.setWindowTitle("Update Instrument")
            msg_box.setText(msg)
            msg_box.show()

        self._exit_gui()

    def _update_db_value_with_frame_data(self, frame: SettingFrame):
        """
        Updates Instrument Server DB with GUI Frame Data
        """

        print('called _update_db_value_with_frame_data')

        # Only update the values that exist (not None)
        if frame.get_frame_dto().value is not None:
            frame_dto = frame.get_frame_dto()
            updated_smt = f"UPDATE {frame_dto.db_table} SET {frame_dto.db_column} = {frame.get_gui_value()} " \
                          f"WHERE {frame_dto.unique_key_column} = '{frame_dto.unique_key_value}';"

            if frame.get_value_data_type() == 'str':
                updated_smt = f"UPDATE {frame_dto.db_table} SET {frame_dto.db_column} = '{frame.get_gui_value()}' " \
                              f"WHERE {frame_dto.unique_key_column} = '{frame_dto.unique_key_value}';"

            with self.flask_app.app_context():
                try:
                    connection = db.get_db()
                    with connection.cursor() as cursor:
                        cursor.execute(updated_smt)
                        connection.commit()

                except Exception as ex:
                    error_msg = f'There was an ERROR updating instrument settings for ' \
                                f'instrument {frame_dto.unique_key_value}: {ex}'
                    self.logger.fatal(error_msg)
                    raise Exception(error_msg)

                finally:
                    # Make sure we always close the connection
                    db.close_db(connection)

    def _exit_gui(self):
        """
        Closes the experiment GUI
        """
        # Reload the parent's GUI Instrument list
        self.parent_gui.get_known_instruments()
        self.close()
