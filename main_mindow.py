from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QCloseEvent

import config
from drivers import NIDAQ
import numpy as np
import database

# don't change - window geometry may be corrupted
NUM_OF_SENSORS = 8
FRAME_VERTICAL_SHIFT = 200
FRAME_HORIZONTAL_SHIFT = 500
DEFAULT_SERIAL_NUM = 'серийный номер'


class ADCThread(QtCore.QThread):
    adc_data = QtCore.pyqtSignal(object)

    def __init__(self, adc_config):
        QtCore.QThread.__init__(self)
        self.adc = NIDAQ.NIDAQ(
            dev_id=adc_config['dev_id'],
            rate=adc_config['rate'],
            acq_time=adc_config['acq_time'],
            channels=adc_config['channels'],
            volt_range=adc_config['range'])
        self.n_channels = len(adc_config['channels'])
        self.quit = False

    def run(self) -> None:
        cycle_buffer = np.zeros((NUM_OF_SENSORS, config.ADC_FILTER_LEN), np.float32)
        cnt = 0
        while not self.quit:
            data = self.adc.get()
            for i in range(NUM_OF_SENSORS):
                cycle_buffer[i, cnt] = data[i]
            cnt = cnt + 1
            if cnt == config.ADC_FILTER_LEN:
                cnt = 0
            data = []
            for i in range(NUM_OF_SENSORS):
                data.append(np.mean(cycle_buffer[i, :]))
            result = ';'.join(['{:0.5f}'.format(d) for d in data])
            self.adc_data.emit(result)
        self.adc.close()

    def stop(self):
        self.quit = True


class TestWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TestWindow, self).__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("KMG tester")
        self.resize(1024, 800)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        font12 = QtGui.QFont()
        font12.setPointSize(12)

        font9 = QtGui.QFont()
        font9.setPointSize(9)

        font12bold = QtGui.QFont()
        font12bold.setPointSize(12)
        font12bold.setBold(True)
        font12bold.setWeight(75)

        font14bold = QtGui.QFont()
        font14bold.setPointSize(14)
        font14bold.setBold(True)
        font14bold.setWeight(100)

        font10 = QtGui.QFont()
        font10.setPointSize(10)

        self.ICON_ON_STATE = QtGui.QPixmap('on.png')
        self.ICON_OFF_STATE = QtGui.QPixmap('off.png')

        self.sensors = [QtWidgets.QFrame(self.centralwidget) for _ in range(NUM_OF_SENSORS)]
        self.serial_nums = [QtWidgets.QLineEdit(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.range_lists = [QtWidgets.QComboBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.sensor_nums = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_forwards = [QtWidgets.QLineEdit(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_forward_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_reverses = [QtWidgets.QLineEdit(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_reverse_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_forward_fixes = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_off_reverse_fixes = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.defects = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_ons = [QtWidgets.QLineEdit(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_on_fixes = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.u_on_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.off_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.label_ons = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.lowers = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.uppers = [QtWidgets.QCheckBox(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.working_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]
        self.reset_button = QtWidgets.QPushButton(self.sensors[3])
        self.store_button = QtWidgets.QPushButton(self.sensors[3])
        self.state_labels = [QtWidgets.QLabel(self.sensors[i]) for i in range(NUM_OF_SENSORS)]

        for i in range(NUM_OF_SENSORS):
            if i > 3:
                horizontal_shift = FRAME_HORIZONTAL_SHIFT
                vertical_shift = (i - 4) * FRAME_VERTICAL_SHIFT
            else:
                horizontal_shift = 0
                vertical_shift = i * FRAME_VERTICAL_SHIFT

            self.sensors[i].setGeometry(QtCore.QRect(horizontal_shift, vertical_shift, 450, 200))
            self.sensors[i].setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            self.sensors[i].setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            self.sensors[i].setObjectName("sensor_{}".format(i))

            self.serial_nums[i].setGeometry(QtCore.QRect(10, 10, 150, 25))
            self.serial_nums[i].setFont(font12)
            self.serial_nums[i].setText(DEFAULT_SERIAL_NUM)
            self.serial_nums[i].setObjectName("serial_num_{}".format(i))

            self.range_lists[i].setGeometry(QtCore.QRect(170, 10, 120, 25))
            self.range_lists[i].setObjectName("range_list_{}".format(i))
            self.range_lists[i].setMaxVisibleItems(5)
            self.range_lists[i].addItems([x['type'] for x in config.SENSOR_TYPES])
            self.range_lists[i].currentIndexChanged.connect(self.on_range_change)

            self.sensor_nums[i].setGeometry(QtCore.QRect(380, 10, 120, 25))
            self.sensor_nums[i].setFont(font14bold)
            self.sensor_nums[i].setText('ключ {}'.format(i + 1))
            self.sensor_nums[i].setObjectName("sensor_num_{}".format(i))

            self.u_off_forwards[i].setGeometry(QtCore.QRect(40, 75, 120, 25))
            self.u_off_forwards[i].setFont(font12)
            self.u_off_forwards[i].setObjectName("u_off_forward_{}".format(i))

            self.u_off_forward_labels[i].setGeometry(QtCore.QRect(40, 55, 120, 20))
            self.u_off_forward_labels[i].setFont(font9)
            self.u_off_forward_labels[i].setText("Прямое Roff, МОм")
            self.u_off_forward_labels[i].setObjectName("u_off_forward_label_{}".format(i))

            self.u_off_reverses[i].setGeometry(QtCore.QRect(200, 75, 120, 25))
            self.u_off_reverses[i].setFont(font12)
            self.u_off_reverses[i].setObjectName("u_off_reverse_{}".format(i))

            self.u_off_reverse_labels[i].setGeometry(QtCore.QRect(200, 55, 120, 20))
            self.u_off_reverse_labels[i].setText("Обратное Roff, МОм")
            self.u_off_reverse_labels[i].setFont(font9)
            self.u_off_reverse_labels[i].setObjectName("u_off_reverse_label_{}".format(i))

            self.u_off_forward_fixes[i].setGeometry(QtCore.QRect(10, 75, 20, 20))
            self.u_off_forward_fixes[i].setText("")
            self.u_off_forward_fixes[i].setObjectName("u_off_forward_fix_{}".format(i))

            self.u_off_reverse_fixes[i].setGeometry(QtCore.QRect(170, 75, 20, 20))
            self.u_off_reverse_fixes[i].setText("")
            self.u_off_reverse_fixes[i].setObjectName("u_off_reverse_fix_{}".format(i))

            self.defects[i].setGeometry(QtCore.QRect(340, 75, 70, 20))
            self.defects[i].setFont(font12bold)
            self.defects[i].setText("Брак")
            self.defects[i].setObjectName("defect_{}".format(i))
            self.defects[i].stateChanged.connect(lambda state, cnt=i: self.on_defect_change(state, cnt))

            self.u_ons[i].setGeometry(QtCore.QRect(40, 140, 120, 25))
            self.u_ons[i].setFont(font12)
            self.u_ons[i].setObjectName("u_on_{}".format(i))

            self.u_on_fixes[i].setGeometry(QtCore.QRect(10, 140, 20, 20))
            self.u_on_fixes[i].setText("")
            self.u_on_fixes[i].setObjectName("u_on_fix_{}".format(i))

            self.u_on_labels[i].setGeometry(QtCore.QRect(40, 120, 120, 20))
            self.u_on_labels[i].setFont(font9)
            self.u_on_labels[i].setText("Ron, Ом")
            self.u_on_labels[i].setObjectName("u_on_label_{}".format(i))

            self.off_labels[i].setGeometry(QtCore.QRect(100, 40, 200, 15))
            self.off_labels[i].setFont(font10)
            self.off_labels[i].setText("Разомкнутый ключ")
            self.off_labels[i].setObjectName("off_label_{}".format(i))

            self.label_ons[i].setGeometry(QtCore.QRect(100, 105, 130, 20))
            self.label_ons[i].setFont(font10)
            self.label_ons[i].setText("Замкнутый ключ")
            self.label_ons[i].setObjectName("label_on_{}".format(i))

            self.lowers[i].setGeometry(QtCore.QRect(230, 140, 100, 20))
            self.lowers[i].setFont(font12bold)
            self.lowers[i].setText("Нижний")
            self.lowers[i].setObjectName("lower_{}".format(i))

            self.uppers[i].setGeometry(QtCore.QRect(330, 140, 100, 20))
            self.uppers[i].setFont(font12bold)
            self.uppers[i].setText("Верхний")
            self.uppers[i].setObjectName("upper_{}".format(i))

            self.working_labels[i].setGeometry(QtCore.QRect(290, 120, 80, 20))
            self.working_labels[i].setFont(font9)
            self.working_labels[i].setText("Сработал")
            self.working_labels[i].setObjectName("working_label_{}".format(i))

            self.state_labels[i].setGeometry(QtCore.QRect(390, 170, 50, 24))
            self.state_labels[i].setPixmap(self.ICON_OFF_STATE)
            self.state_labels[i].setObjectName("state_label_{}".format(i))

        self.store_button.setGeometry(QtCore.QRect(200, 170, 75, 25))
        self.store_button.setText("Запись")
        self.store_button.setObjectName("store_button")
        self.store_button.clicked.connect(self.store_results)

        self.reset_button.setGeometry(QtCore.QRect(40, 170, 75, 25))
        self.reset_button.setText("Сброс")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_form)

        self.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.on_range_change()

        adc_config = {
            'dev_id': config.ADC_DEV,
            'rate': config.ADC_FREQ,
            'acq_time': config.ADC_TIME_ACQ,
            'channels': config.ADC_CHANNELS,
            'range': config.ADC_RANGE,
        }
        self.fix = False
        self.adc = ADCThread(adc_config=adc_config)
        self.adc.start()
        self.adc.adc_data.connect(self.update_fields)
        self.u_power = 0

    def store_results(self):
        db = database.SensorDataBase()
        for i in range(NUM_OF_SENSORS):
            if self.u_on_fixes[i].isChecked() \
                    and self.u_off_reverse_fixes[i].isChecked() \
                    and self.u_off_forward_fixes[i].isChecked() \
                    and self.serial_nums[i].text() != DEFAULT_SERIAL_NUM:
                serial_num = self.serial_nums[i].text()
                indx_type = self.range_lists[i].currentIndex()
                sensor_type = config.SENSOR_TYPES[indx_type]['type']
                params = {
                    'threshold': config.SENSOR_TYPES[indx_type]['threshold'],
                    'power_voltage': self.u_power,
                    'test_resistivity': config.RH,
                    'on_resistivity': float(self.u_ons[i].text()),
                    'on_voltage': float(self.u_ons[i].toolTip()),
                    'off_resistivity_forward': float(self.u_off_forwards[i].text()),
                    'off_voltage_forward': float(self.u_off_forwards[i].toolTip()),
                    'off_resistivity_reverse': float(self.u_off_reverses[i].text()),
                    'off_voltage_reverse': float(self.u_off_reverses[i].toolTip()),
                    'upper_triggered': 1 if self.uppers[i].isChecked() else 0,
                    'upper_acceleration': config.SENSOR_TYPES[indx_type]['upper_limit'],
                    'lower_triggered': 1 if self.lowers[i].isChecked() else 0,
                    'lower_acceleration': config.SENSOR_TYPES[indx_type]['lower_limit'],
                    'defect': 1 if self.defects[i].isChecked() else 0,
                    'test_connector': i + 1,
                }
                db.add_sensor(sensor_type, serial_num)
                if params['defect'] == 1:
                    db.add_defect(sensor_type, serial_num)
                db.add_parameters(sensor_type, serial_num, params)
        db.close()
        alert = QtWidgets.QMessageBox(self)
        alert.setWindowTitle('Сохранено')
        alert.setText('Сохранены результаты только с зафиксированными полями\n и новым серийным номером!')
        alert.exec()

    def reset_form(self):
        for i in range(NUM_OF_SENSORS):
            self.u_off_forward_fixes[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.u_off_reverse_fixes[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.u_on_fixes[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.defects[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.lowers[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.uppers[i].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.serial_nums[i].setText(DEFAULT_SERIAL_NUM)
            self.range_lists[i].setCurrentIndex(0)

    def on_defect_change(self, new_state, origin):
        if self.defects[origin].isChecked():
            self.u_on_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Checked)
            self.u_off_reverse_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Checked)
            self.u_off_forward_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Checked)
        else:
            self.u_on_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.u_off_reverse_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)
            self.u_off_forward_fixes[origin].setCheckState(QtCore.Qt.CheckState.Checked.Unchecked)

    def on_range_change(self):
        for i in range(NUM_OF_SENSORS):
            indx = self.range_lists[i].currentIndex()
            accel_low = config.SENSOR_TYPES[indx]['lower_limit']
            accel_high = config.SENSOR_TYPES[indx]['upper_limit']
            self.lowers[i].setText('{:0.2f}g'.format(accel_low))
            self.uppers[i].setText('{:0.2f}g'.format(accel_high))

    def update_fields(self, data):
        adc_data = data.split(';')
        u_plus = 5  # (float(adc_data[NUM_OF_SENSORS]))
        u_minus = 0  # (float(adc_data[NUM_OF_SENSORS + 1]))
        u_power = (u_plus - u_minus)
        u_out = [(float(adc_data[i]) - u_minus) for i in range(NUM_OF_SENSORS)]
        if u_power > 0:
            u_out = [x if x > 0.01 else 0.01 for x in u_out]
            u_out = [x if x < u_power else u_power for x in u_out]
        else:
            u_out = [x if x < -0.01 else -0.01 for x in u_out]
            u_out = [x if x > u_power else u_power for x in u_out]
        resistivity = []
        for i in range(NUM_OF_SENSORS):
            try:
                resistivity.append(u_power / u_out[i] * config.RH - config.RH)
            except ZeroDivisionError:
                resistivity.append(100e6)
        self.u_power = u_power
        for i in range(NUM_OF_SENSORS):
            if not self.u_off_forward_fixes[i].isChecked():
                self.u_off_forwards[i].setText('{:0.4f}'.format(resistivity[i] / 1e6))
                self.u_off_forwards[i].setToolTip('{:0.4f}'.format(u_out[i]))
            if not self.u_off_reverse_fixes[i].isChecked():
                self.u_off_reverses[i].setText('{:0.4f}'.format(resistivity[i] / 1e6))
                self.u_off_reverses[i].setToolTip('{:0.4f}'.format(u_out[i]))
            if not self.u_on_fixes[i].isChecked():
                self.u_ons[i].setText('{:0.1f}'.format(resistivity[i]))
                self.u_ons[i].setToolTip('{:0.4f}'.format(u_out[i]))
            if resistivity[i] < config.MAX_RESISTIVITY_ON_STATE:
                self.state_labels[i].setPixmap(self.ICON_ON_STATE)
                pass
            else:
                self.state_labels[i].setPixmap(self.ICON_OFF_STATE)
                pass

    def closeEvent(self, event: QCloseEvent):
        self.adc.stop()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = TestWindow()
    ui.show()
    sys.exit(app.exec())
