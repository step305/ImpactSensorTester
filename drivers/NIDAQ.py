import nidaqmx
from nidaqmx import constants
import numpy as np
from nidaqmx.constants import TerminalConfiguration

DEFAULT_DEV_ID = 'Dev5'
DEFAULT_RATE = 1000
DEFAULT_ACQUISITION_TIME = 10.0
DEFAULT_CHANNELS = (0, 1, 2, 3, 4, 5, 6, 7, 8)


class NIDAQ:
    def __init__(self,
                 dev_id=DEFAULT_DEV_ID,
                 rate=DEFAULT_RATE,
                 acq_time=DEFAULT_ACQUISITION_TIME,
                 channels=DEFAULT_CHANNELS,
                 volt_range=10):
        """
        Args:
            dev_id (): String, DevID of NIDAQ
            rate (): sample rate, Hz
            acq_time (): time to acquire in one point, sec
            channels (): list of channels number, ex. [0, 2, 4]
        """
        self.adc_task = nidaqmx.Task()
        self.dev_id = dev_id
        self.rate = int(rate)
        self.samples_per_channel = int(self.rate * acq_time)
        for channel in channels:
            self.adc_task.ai_channels.add_ai_voltage_chan('{}/ai{:d}'.format(self.dev_id, channel),
                                                          terminal_config=TerminalConfiguration.RSE,
                                                          min_val=-volt_range, max_val=volt_range)
        self.adc_task.timing.cfg_samp_clk_timing(rate=self.rate,
                                                 sample_mode=constants.AcquisitionType.FINITE,
                                                 samps_per_chan=self.samples_per_channel)

    def get(self):
        """
        get ADC measurements
        Returns:
            data = list of lists^ len(data0 == len(ADC_CHANNELS), len(data[0]) == acq_time * rate
        """
        data = self.adc_task.read(number_of_samples_per_channel=self.samples_per_channel,
                                  timeout=self.samples_per_channel / self.rate * 1.6)
        return [np.mean(d) for d in data]

    def close(self):
        self.adc_task.close()


if __name__ == '__main__':
    adc = NIDAQ()
    dat = adc.get()
    print([np.mean(d) for d in dat])
    print([np.std(d) for d in dat])
    adc.close()
