from PyQt6 import QtCore, QtWidgets as QtW
from PyQt6.QtGui import QFont, QAction, QCursor
import logging

from PyQt6.QtWidgets import QLineEdit, QComboBox, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QFileDialog, \
    QSizePolicy, QHeaderView


###################################################################################
# SettingFrameDTO
###################################################################################
class SettingFrameDTO:
    def __init__(self, label, value, db_table, db_column, unique_key_column, unique_key_value):
        self._label = label
        self._value = value
        self._db_table = db_table
        self._db_column = db_column
        self._unique_key_column = unique_key_column
        self._unique_key_value = unique_key_value
        self._cascade_update = False

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, new_label):
        self._label = new_label

    @property
    def value(self):
        return self._value

    @property
    def db_table(self):
        return self._db_table

    @property
    def db_column(self):
        return self._db_column

    @property
    def unique_key_column(self):
        return self._unique_key_column

    @property
    def unique_key_value(self):
        return self._unique_key_value

    @property
    def cascade_update(self):
        return self._cascade_update

    @cascade_update.setter
    def cascade_update(self, flag):
        self._cascade_update = flag

###################################################################################
# SettingFrame
###################################################################################
class SettingFrame(QtW.QFrame):
    def __init__(self, frame_dto: SettingFrameDTO, logger: logging.Logger):
        super().__init__()
        self.frame_dto = frame_dto
        self.logger = logger
        self.label_weight = 1
        self.value_weight = 2

        # Set basic layout
        self.layout = QtW.QHBoxLayout()
        self.label = QtW.QLabel()
        self.label.setText(frame_dto.label)

        font = QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setMaximumHeight(25)
        self.layout.addWidget(self.label, self.label_weight)

    def get_frame_dto(self):
        return self.frame_dto

    def get_gui_value(self):
        pass

    def get_value_data_type(self):
        pass

    def reset(self):
        pass


class StringSettingFrame(SettingFrame):
    def __init__(self, frame_dto: SettingFrameDTO, logger: logging.Logger):
        super().__init__(frame_dto, logger)
        self.stringBox = QLineEdit()
        self.stringBox.setText(str(frame_dto.value))
        self.layout.addWidget(self.stringBox, self.value_weight)
        self.setLayout(self.layout)

    def reset(self):
        self.stringBox.setText(str(self.frame_dto.value))

    def get_gui_value(self):
        return self.stringBox.text()

    def get_value_data_type(self):
        return 'str'


class ComboBoxSettingFrame(SettingFrame):
    def __init__(self, frame_dto: SettingFrameDTO, combo_box_contents: list, logger: logging.Logger):
        super().__init__(frame_dto, logger)

        self.combo_box = QComboBox()
        self.combo_box.addItems(combo_box_contents)

        interface_combo_index = self.combo_box.findText(frame_dto.value)
        self.combo_box.setCurrentIndex(interface_combo_index)

        self.layout.addWidget(self.combo_box, self.value_weight)
        self.setLayout(self.layout)

    def reset(self):
        interface_combo_index = self.combo_box.findText(self.frame_dto.value)
        self.combo_box.setCurrentIndex(interface_combo_index)

    def get_gui_value(self):
        return self.combo_box.currentText()

    def get_value_data_type(self):
        return 'str'


class TwoRadioButtonSettingFrame(SettingFrame):
    def __init__(self, frame_dto: SettingFrameDTO, logger: logging.Logger):
        super().__init__(frame_dto, logger)

        # Create button group and connect to method
        self.button_group = QtW.QButtonGroup()
        self.button_group.setExclusive(True)

        # add radio buttons to group
        self.true_radio_button = QtW.QRadioButton("True")
        self.button_group.addButton(self.true_radio_button)
        self.false_radio_button = QtW.QRadioButton("False")
        self.button_group.addButton(self.false_radio_button)

        self.true_radio_button.setChecked(bool(frame_dto.value))
        self.false_radio_button.setChecked(not bool(frame_dto.value))

        # create local layout and button group widget so that the spacing is correct
        h_layout = QtW.QHBoxLayout()
        h_layout.addWidget(self.true_radio_button)
        h_layout.addWidget(self.false_radio_button)

        self.button_group_widget = QtW.QWidget()
        self.button_group_widget.setLayout(h_layout)
        self.button_group_widget.setFixedHeight(40)

        self.layout.addWidget(self.button_group_widget, self.value_weight)
        self.setLayout(self.layout)

    def reset(self):
        self.true_radio_button.setChecked(bool(self.frame_dto.value))
        self.false_radio_button.setChecked(not bool(self.frame_dto.value))

    def get_gui_value(self):
        return self.true_radio_button.isChecked()

    def get_value_data_type(self):
        return 'bool'


class FileDialogSettingFrame(SettingFrame):
    def __init__(self, frame_dto: SettingFrameDTO, logger: logging.Logger):
        super().__init__(frame_dto, logger)

        # Box 1 for driver file input
        self.path_line = QLineEdit()
        self.path_line.setText(frame_dto.value)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.get_file_path)

        file_input_hbox = QHBoxLayout()
        file_input_hbox.addWidget(self.path_line)
        file_input_hbox.addWidget(self.file_button)
        self.layout.addLayout(file_input_hbox, self.value_weight)
        self.setLayout(self.layout)

    def reset(self):
        self.path_line.setText(self.frame_dto.value)

    def get_file_path(self):
        file_filter = 'Configuration File (*.ini);; Python File (*.py)'
        initial_filter = 'Configuration File (*.ini)'
        file_name = QFileDialog.getOpenFileName(parent=self, caption="Select File", directory="C:\\",
                                                filter=file_filter,
                                                initialFilter=initial_filter)

        if file_name[0]:
            self.path_line.setText(file_name[0])

    def get_gui_value(self):
        return self.path_line.text()

    def get_value_data_type(self):
        return 'str'


class IntegerSettingFrame(SettingFrame):
    def __init__(self, frame_dto: SettingFrameDTO, min_int, max_int, logger: logging.Logger):
        super().__init__(frame_dto, logger)

        self.intSpinBox = QtW.QSpinBox()
        self.intSpinBox.setMaximum(max_int)
        self.intSpinBox.setMinimum(min_int)

        if frame_dto.value:
            self.intSpinBox.setValue(int(frame_dto.value))

        self.layout.addWidget(self.intSpinBox, self.value_weight)
        self.setLayout(self.layout)

    def reset(self):
        if self.frame_dto.value:
            self.intSpinBox.setValue(int(self.frame_dto.value))

    def get_gui_value(self):
        return self.intSpinBox.value()

    def get_value_data_type(self):
        return 'int'


###################################################################################
# SettingsGroupBox
###################################################################################
class SettingsGroupBox(QtW.QGroupBox):
    def __init__(self, setting_group_name: str, frames: list[SettingFrame]):
        super().__init__()
        self.my_frames = frames
        self.layout = QtW.QVBoxLayout()

        self.label = QtW.QLabel()
        self.label.setText(setting_group_name)
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setMaximumHeight(25)
        self.layout.addWidget(self.label)

        for frame in frames:
            self.layout.addWidget(frame)

        self.layout.stretch(1)
        self.setLayout(self.layout)

    def rest_all_my_frames(self):
        for frame in self.my_frames:
            frame.reset()
