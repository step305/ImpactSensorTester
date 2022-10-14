import database
import report_config
import pandas


if __name__ == '__main__':
    print('Report Generator')
    db = database.SensorDataBase()
    data = []
    for sensor in report_config.SENSOR:
        params = db.get_params(sensor['type'], sensor['serial_num'])
        if params:
            data.append(params)
            keys = list(params.keys())
    if data:
        df = pandas.DataFrame(data, columns=keys)
        df.set_index('Серийный номер', inplace=True)
        df.to_excel(report_config.REPORT_FILE, sheet_name='Результаты')
