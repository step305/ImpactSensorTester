import sqlite3
import datetime


class SensorDataBase:
    def __init__(self, db_path='kmg_database.db'):
        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            req = 'select sqlite_version();'
            self.cursor.execute(req)
            resp = self.cursor.fetchall()
            print(resp)

            req = 'CREATE TABLE IF NOT EXISTS sensors (' \
                  'id INTEGER PRIMARY KEY, ' \
                  'serial_num TEXT NOT NULL, ' \
                  'sensor_type TEXT NOT NULL, ' \
                  'comment TEXT, ' \
                  'shipped_to TEXT, ' \
                  'UNIQUE (sensor_type, serial_num) ON CONFLICT IGNORE' \
                  ');'
            self.cursor.execute(req)
            self.connection.commit()

            req = 'CREATE TABLE IF NOT EXISTS defects (' \
                  'id INTEGER PRIMARY KEY, ' \
                  'serial_num TEXT NOT NULL, ' \
                  'sensor_type TEXT NOT NULL, ' \
                  'date TIMESTAMP NOT NULL, ' \
                  'comment TEXT, ' \
                  'UNIQUE (sensor_type, serial_num) ON CONFLICT IGNORE' \
                  ');'
            self.cursor.execute(req)
            self.connection.commit()

            req = 'CREATE TABLE IF NOT EXISTS parameters (' \
                  'id INTEGER PRIMARY KEY,' \
                  'serial_num TEXT NOT NULL, ' \
                  'sensor_type TEXT NOT NULL, ' \
                  'threshold REAL, ' \
                  'date TIMESTAMP NOT NULL, ' \
                  'power_voltage REAL, ' \
                  'test_resistivity REAL, ' \
                  'on_resistivity REAL, ' \
                  'on_voltage REAL, ' \
                  'off_resistivity_forward REAL, ' \
                  'off_voltage_forward REAL, ' \
                  'off_resisitivity_reverse REAL, ' \
                  'off_voltage_reverse REAL, ' \
                  'upper_triggered INTEGER, ' \
                  'upper_acceleration REAL, ' \
                  'lower_triggered INTEGER, ' \
                  'lower_acceleration REAL, ' \
                  'defect INTEGER, ' \
                  'test_connector INTEGER, ' \
                  'comment TEXT, ' \
                  'UNIQUE (sensor_type, serial_num) ON CONFLICT IGNORE' \
                  ');'
            self.cursor.execute(req)
            self.connection.commit()

            self.cursor.close()

        except sqlite3.Error as error:
            print('Init:', error)

    def add_sensor(self, sensor_type, serial_num):
        try:
            self.cursor = self.connection.cursor()
            req = 'INSERT INTO sensors (serial_num, sensor_type) VALUES (?, ?);'
            self.cursor.execute(req, (serial_num, sensor_type,))
            self.connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Add sensor:', error)

    def add_defect(self, sensor_type, serial_num):
        try:
            self.cursor = self.connection.cursor()
            req = 'INSERT INTO defects (serial_num, sensor_type, date) VALUES (?, ?, ?);'
            self.cursor.execute(req, (serial_num, sensor_type, datetime.datetime.now(),))
            self.connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Add defect', error)

    def add_parameters(self, sensor_type, serial_num, params):
        try:
            self.cursor = self.connection.cursor()
            req = 'INSERT INTO parameters (serial_num, ' \
                  'sensor_type, ' \
                  'date, ' \
                  'threshold, ' \
                  'power_voltage, ' \
                  'test_resistivity, ' \
                  'on_resistivity, ' \
                  'on_voltage, ' \
                  'off_resistivity_forward, ' \
                  'off_voltage_forward, ' \
                  'off_resisitivity_reverse, ' \
                  'off_voltage_reverse, ' \
                  'upper_triggered, ' \
                  'upper_acceleration, ' \
                  'lower_triggered, ' \
                  'lower_acceleration, ' \
                  'defect, ' \
                  'test_connector' \
                  ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
            self.cursor.execute(req,
                                (
                                    serial_num,
                                    sensor_type,
                                    datetime.datetime.now(),
                                    params['threshold'],
                                    params['power_voltage'],
                                    params['test_resistivity'],
                                    params['on_resistivity'],
                                    params['on_voltage'],
                                    params['off_resistivity_forward'],
                                    params['off_voltage_forward'],
                                    params['off_resistivity_reverse'],
                                    params['off_voltage_reverse'],
                                    params['upper_triggered'],
                                    params['upper_acceleration'],
                                    params['lower_triggered'],
                                    params['lower_acceleration'],
                                    params['defect'],
                                    params['test_connector'],
                                ))
            self.connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Add params', error)

    def get_params(self, sensor_type, serial_num):
        try:
            self.cursor = self.connection.cursor()
            req = 'SELECT ' \
                  'date, ' \
                  'threshold, ' \
                  'power_voltage, ' \
                  'test_resistivity, ' \
                  'on_resistivity, ' \
                  'on_voltage, ' \
                  'off_resistivity_forward, ' \
                  'off_voltage_forward, ' \
                  'off_resisitivity_reverse, ' \
                  'off_voltage_reverse, ' \
                  'upper_triggered, ' \
                  'upper_acceleration, ' \
                  'lower_triggered, ' \
                  'lower_acceleration, ' \
                  'defect, ' \
                  'test_connector ' \
                  'FROM parameters WHERE sensor_type = ? AND serial_num = ?;'
            self.cursor.execute(req, (sensor_type, serial_num,))
            params = self.cursor.fetchall()
            self.cursor.close()
            if params:
                result = {
                    'Тип': sensor_type,
                    'Серийный номер': serial_num,
                    'Дата испытания': params[0][0],
                    'Порог срабатывания, g': params[0][1],
                    'Напряжение питания, В': params[0][2],
                    'Тестовое сопротивление, кОм': round(params[0][3] / 1e3, 2),
                    'Сопротивление замкнутого ключа,Ом': round(params[0][4], 2),
                    'Uвых (замкнутый ключ), мВ': round(params[0][5] * 1e3, 1),
                    'Сопротивление разомкнутого ключа (прямое), МОм': round(params[0][6], 6),
                    'Uвых (разомкнутый ключ, прямое), мВ': round(params[0][7] * 1e3, 1),
                    'Сопротивление разомкнутого ключа (обратное), МОм': round(params[0][8], 6),
                    'Uвых (разомкнутый ключ, обратное), мВ': round(params[0][9] * 1e3, 1),
                    'Сработал (верх), g': '{:0.2}g'.format(params[0][11]) if params[0][10] == 1 else 'нет',
                    'Сработал (низ)': '{:0.2}g'.format(params[0][13]) if params[0][12] == 1 else 'нет',
                    'Годен': 'да' if params[0][14] == 0 and params[0][4] < 200 and params[0][6] > 2
                                     and params[0][8] > 2 else 'нет',
                    'Номер контактного устройства': params[0][15],
                }
            else:
                result = {}
            return result
        except sqlite3.Error as error:
            print('Get Params:', error)
            return ()

    def close(self):
        if self.connection:
            self.connection.close()
