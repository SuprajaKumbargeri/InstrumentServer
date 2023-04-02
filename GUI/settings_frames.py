from PyQt6.QtWidgets import QFrame, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSpinBox, QLineEdit


class GeneralSettingsGroupBox(QGroupBox):
    def __init__(self, general_settings: dict):
        super().__init__()
        self.gen_settings = general_settings

        self.main_layout = QVBoxLayout()

        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel(self.gen_settings['cute_name'])


class VISASettingsGroupBox(QGroupBox):
    def __init__(self, visa_settings: dict):
        super().__init__()
        self.visa_settings = visa_settings
        self.main_layout = QVBoxLayout()
        self.label_weight = 1
        self.edit_weight = 2

        # Add VISA frames
        use_visa_frame = self._build_use_visa_frame()
        self.main_layout.addWidget(use_visa_frame)

        reset_frame = self._build_use_visa_frame()
        self.main_layout.addWidget(reset_frame)

        query_errors_frame = self._build_query_error_frame()
        self.main_layout.addWidget(query_errors_frame)

        error_bit_mask_frame = self._build_error_bit_mask_frame()
        self.main_layout.addWidget(error_bit_mask_frame)

        error_cmd_frame = self._build_error_cmd_frame()
        self.main_layout.addWidget(error_cmd_frame)

        init_frame = self._build_init_frame()
        self.main_layout.addWidget(init_frame)

        final_frame = self._build_final_frame()
        self.main_layout.addWidget(final_frame)

        true_frame = self._build_str_true_frame()
        self.main_layout.addWidget(true_frame)

        false_frame = self._build_str_false_frame()
        self.main_layout.addWidget(false_frame)

        self.setLayout(self.main_layout)


    def _build_use_visa_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Use VISA')
        self.use_visa_checkbox = QCheckBox()
        self.use_visa_checkbox.setChecked(self.visa_settings['use_visa'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.use_visa_checkbox, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_reset_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Reset')
        self.reset_checkbox = QCheckBox()
        self.reset_checkbox.setChecked(self.visa_settings['reset'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.reset_checkbox, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_query_error_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Query Errors')
        self.query_checkbox = QCheckBox()
        self.query_checkbox.setChecked(self.visa_settings['query_instr_errors'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.query_checkbox, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_error_bit_mask_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Error Bit Mask')

        self.bit_mask = QSpinBox()
        self.bit_mask.setMaximum(255)
        self.bit_mask.setMinimum(0)
        self.bit_mask.setValue(self.visa_settings['error_bit_mask'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.bit_mask, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_error_cmd_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Error Command')

        self.error_cmd = QLineEdit()
        self.error_cmd.setText(self.visa_settings['error_cmd'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.error_cmd, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_init_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Init Command')

        self.init = QLineEdit()
        self.init.setText(self.visa_settings['init'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.init, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_final_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Final Command')

        self.final = QLineEdit()
        self.final.setText(self.visa_settings['final'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.final, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_str_true_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Instrument True Value')

        self.true_value = QLineEdit()
        self.true_value.setText(self.visa_settings['str_true'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.true_value, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_str_false_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('Instrument False Value')

        self.false_value = QLineEdit()
        self.false_value.setText(self.visa_settings['str_false'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.false_value, self.edit_weight)
        frame.setLayout(layout)
        return frame

    def _build_str_value_out_frame(self):
        frame = QFrame()
        layout = QHBoxLayout()
        label = QLabel('String Value Out')

        self.str_value_out = QLineEdit()
        self.str_value_out.setText(self.visa_settings['str_value_out'])

        layout.addWidget(label, self.label_weight)
        layout.addWidget(self.str_value_out, self.edit_weight)
        frame.setLayout(layout)
        return frame

