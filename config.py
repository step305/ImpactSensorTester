SENSOR_TYPES = (
    {
        'type': 'тип_1',
        'threshold': 110,
        'upper_limit': 110 * 1.2,
        'lower_limit': 110 * 0.8 - 1,
    },
    {
        'type': 'тип_2',
        'threshold': 120,
        'upper_limit': 120 * 1.2,
        'lower_limit': 120 * 0.8 - 1,
    },
    {
        'type': 'тип_3',
        'threshold': 110,
        'upper_limit': 110 * 1.3,
        'lower_limit': 110 * 0.7 - 1,
    },
    {
        'type': 'тип_4',
        'threshold': 7,
        'upper_limit': 7 * 1.2,
        'lower_limit': 7 * 0.8 - 0.25,
    },
    {
        'type': 'тип_5',
        'threshold': 100,
        'upper_limit': 100 * 1.3,
        'lower_limit': 100 * 0.7 - 1,
    },
)

ADC_CHANNELS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)  # 0-7 for KNG, 8 for power "+", 9 - for power "-"
ADC_FREQ = 1000  # Hz
ADC_TIME_ACQ = 0.2  # sec
ADC_DEV = 'Dev1'
ADC_RANGE = 10  # Volt
ADC_FILTER_LEN = 10
RH = 10000  # test resistor, Ohm
MAX_RESISTIVITY_ON_STATE = 200  # resistivity when KMG is on
