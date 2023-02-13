from picoscope import *
import requests
import time
import matplotlib.pyplot as plt
import numpy as np

class PicoscopeManager:
    def __init__(self, driver):
        self._initialize_driver(driver)
        self._name = self._driver['general_settings']['name']
        self._ps = self._initialize_picoscope()
        # self._startup()

    '''Communicates with instrument server to get driver for instrument'''

    def _initialize_driver(self, driver):
        # implementation will likely change
        url = r'http://localhost:5000/driverParser/'
        response = requests.get(url, data={'driverPath': driver})

        if 300 > response.status_code >= 200:
            self._driver = dict(response.json())
        else:
            response.raise_for_status()

    '''Initializes Picoscope'''

    def _initialize_picoscope(self):
        # string passed through in VISA form
        ps = ps6000.PS6000(serialNumber=None, connect=True)
        return ps

    '''destructor - close picoscope'''

    def __del__(self):
        self._close()

    '''Closes Picoscope. Should be called when done using PicoscopeManager'''

    def _close(self):
        # self._ps.stop()
        self._ps.close()

    @property
    def name(self):
        return self._name

    @property
    def model(self):
        return self.ask(self._driver['model_and_options']['model_cmd'])

    @property
    def options(self):
        return self.ask(self._driver['model_and_options']['option_cmd'])

    @property
    def quantities(self):
        return self._driver['quantities']

    '''Set's default value for given quantity'''

    def _set_default_value(self, quantity):
        if self.quantities[quantity]['def_value']:
            self[quantity] = self.quantities[quantity]['def_value']

    def _startup(self):
        # Check models supported by driver
        if self._driver['model_and_options']['check_model']:
            model = self.model
            # TODO: Check if model matches given one in driver

        for quantity in self.quantities.keys():
            self._set_default_value(quantity)

        # store def values from driver to db

    def get_value(self, quantity):
        # instead of getting value from quantities dict, get from db
        return self.quantities[quantity]['def_value']  # self.ask(self.quantities[quantity]['get_cmd'])

    def set_value(self, quantity, value):
        lower_lim = self.quantities[quantity]['low_lim']
        upper_lim = self.quantities[quantity]['high_lim']

        # check limits
        if not lower_lim == '-INF' and value < float(lower_lim):
            raise ValueError(f"{value} is lower than {quantity}'s lower limit of {lower_lim}.")
        if not upper_lim == '+INF' and value < float(upper_lim):
            raise ValueError(f"{value} is higher than {quantity}'s upper limit of {upper_lim}.")

        self.quantities[quantity]["def_value"] = value

        # instead of assigin value to def_value, update driver table in SQL db

    def __getitem__(self, quantity):
        return self.get_value(quantity)

    def __setitem__(self, quantity, value):
        self.set_value(quantity, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _signal_generator(self):
        frequency = self.get_value('Frequency')
        offset_voltage = self.get_value('Offset')
        pk_to_pk = self.get_value('Amplitude')
        wave_type = self.get_value('Wave Type')

        waveform_desired_duration = 1 / frequency
        obs_duration = 10 * waveform_desired_duration
        sampling_interval = obs_duration / 4096

        (actualSamplingInterval, nSamples, maxSamples) = self._ps.setSamplingInterval(
            sampling_interval, obs_duration)
        print("Sampling interval = %f ns" % (actualSamplingInterval * 1E9))
        print("Taking  samples = %d" % nSamples)
        print("Maximum samples = %d" % maxSamples)

        self._ps.setChannel('A', 'DC', 2.0, 0.0, True, False)
        self._ps.setSimpleTrigger('A', 0.0, 'Rising', delay=0, timeout_ms=100,
                                  enabled=True)

        self._ps.setSigGenBuiltInSimple(offsetVoltage=offset_voltage, pkToPk=pk_to_pk, waveType=wave_type,
                                        frequency=1 / waveform_desired_duration,
                                        shots=1, triggerType="Rising",
                                        triggerSource="None")

        # take the desired waveform
        # This measures all the channels that have been enabled
        self._ps.runBlock()
        self._ps.waitReady()
        print("Done waiting for trigger")
        time.sleep(10)
        self._ps.runBlock()
        self._ps.waitReady()

        response = dataA = self._ps.getDataV('A', nSamples, returnOverflow=False)
        dataTimeAxis = np.arange(nSamples) * actualSamplingInterval

        plt.plot(dataTimeAxis, dataA, label="Waveform")
        plt.grid(True, which='major')
        plt.title("Picoscope 6000 waveforms")
        plt.ylabel("Voltage (V)")
        plt.xlabel("Time (ms)")
        plt.legend()
        plt.savefig("test.png")
        plt.close()
        print("plt.show done")

        return response.tolist()

    def _arbitrary_waveform_generator(self, frequency, waveformAmplitude, waveformOffset):
        # waveform_desired_duration = 1E-3
        waveform_desired_duration = 1 / frequency
        obs_duration = 3 * waveform_desired_duration
        sampling_interval = obs_duration / 4096

        (actualSamplingInterval, nSamples, maxSamples) = \
            self._ps.setSamplingInterval(sampling_interval, obs_duration)
        print("Sampling interval = %f ns" % (actualSamplingInterval * 1E9))
        print("Taking  samples = %d" % nSamples)
        print("Maximum samples = %d" % maxSamples)

        # waveformAmplitude = 1.5
        # waveformOffset = 0
        x = np.linspace(-1, 1, num=self._ps.AWGMaxSamples, endpoint=False)
        # generate an interesting looking waveform
        waveform = waveformOffset + (x / 2 + (x ** 2) / 2) * waveformAmplitude

        (waveform_duration, deltaPhase) = self._ps.setAWGSimple(
            waveform, waveform_desired_duration, offsetVoltage=0.0,
            indexMode="Dual", triggerSource='None')

        # the setChannel command will chose the next largest amplitude
        # BWLimited = 1 for 6402/6403, 2 for 6404, 0 for all
        channelRange = self._ps.setChannel('A', 'DC', waveformAmplitude, 0.0,
                                           enabled=True, BWLimited=False)

        print("Chosen channel range = %d" % channelRange)

        self._ps.setSimpleTrigger('A', 1.0, 'Falling', delay=0, timeout_ms=100,
                                  enabled=True)

        self._ps.runBlock()
        self._ps.waitReady()
        print("Waiting for awg to settle.")
        time.sleep(2.0)
        self._ps.runBlock()
        self._ps.waitReady()
        print("Done waiting for trigger")
        response = dataA = self._ps.getDataV('A', nSamples, returnOverflow=False)

        # dataTimeAxis = np.arange(nSamples) * actualSamplingInterval

        # plt.ion()
        # plt.figure()
        # plt.hold(True)
        # plt.plot(dataTimeAxis, dataA, label="Clock")
        # plt.grid(True, which='major')
        # plt.title("Picoscope 6000 waveforms")
        # plt.ylabel("Voltage (V)")
        # plt.xlabel("Time (ms)")
        # plt.legend()
        # plt.show()
        return response.tolist()
