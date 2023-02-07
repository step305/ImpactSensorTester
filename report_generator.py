import database
import report_config
import pandas

if __name__ == '__main__':
    print('Report Generator')
    db = database.SensorDataBase()
    data = []
    if report_config.SENSOR == 'all':
        sensors_all = []
        for s in db.all():
            sensors_all.append({'type': s[1], 'serial_num': s[0]})
    else:
        sensors_all = report_config.SENSOR
    for sensor in sensors_all:
        params = db.get_params(sensor['type'], sensor['serial_num'])
        if params:
            if (params['Сопротивление замкнутого ключа,Ом'] <= 200 and
                    params['Сопротивление разомкнутого ключа (прямое), МОм'] > 2 and
                    params['Сопротивление разомкнутого ключа (обратное), МОм'] > 2 and
                    (not params['Сработал (верх), g'] == 'нет') and
                    params['Сработал (низ)'] == 'нет'):
                params['Годен'] = 'да'
            data.append(params)
            keys = list(params.keys())
    if data:
        df = pandas.DataFrame(data, columns=keys)
        df.set_index('Серийный номер', inplace=True)
        df.to_excel(report_config.REPORT_FILE, sheet_name='Результаты')
