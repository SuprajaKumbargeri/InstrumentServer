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
        self._ps.stop()
        self._ps.close()

    def _signal_generator(self, waveform_desired_duration, offset_voltage, pk_to_pk, wave_type):
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
        # dataTimeAxis = np.arange(nSamples) * actualSamplingInterval
        #
        # plt.plot(dataTimeAxis, dataA, label="Waveform")
        # plt.grid(True, which='major')
        # plt.title("Picoscope 6000 waveforms")
        # plt.ylabel("Voltage (V)")
        # plt.xlabel("Time (ms)")
        # plt.legend()
        # plt.savefig("test.png")
        # plt.close()
        # print("plt.show done")
        return response.tolist()

    def _arbitrary_waveform_generator(self, waveform_desired_duration, waveformAmplitude, waveformOffset):
        # waveform_desired_duration = 1E-3
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



