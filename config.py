SENSOR_TYPES = ['тип 1', 'тип 2', 'тип 3', 'тип 4']  # KMG titles (text of type)
SENSOR_TYPES_THRESHOLD = [100, 100, 110, 7]  # KMG threshold - working acceleration
TOLERANCES = [10, 20, 30]  # KMG tolerance %
TOLERANCE_DELTA = 1  # delta for lower range
ADC_CHANNELS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)  # 0-7 for KNG, 8 for power "+", 9 - for power "-"
ADC_FREQ = 1000  # Hz
ADC_TIME_ACQ = 0.2  # sec
ADC_DEV = 'Dev1'
ADC_RANGE = 10  # Volt
RH = 10000  # test resistor, Ohm
MAX_RESISTIVITY_ON_STATE = 200  # resistivity when KMG is on
