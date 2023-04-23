#!/usr/bin/env python
from picoscope import *
from Instrument.instrument_manager import InstrumentManager
import numpy as np
import time
import matplotlib.pyplot as plt


class PicoscopeManager(InstrumentManager):
    """ This class implements the picoscope"""

    def __init__(self, name, driver, logger):
        self._name = name
        self._driver = driver
        self._logger = logger
        self._ps = self._initialize_instrument()

    def _initialize_instrument(self):
        self._logger.debug(f"'Initializing {self._name}'...'")
        ps = ps6000.PS6000(serialNumber=None, connect=True)
        return ps

    def get_value(self, quantity):
        url = r'http://localhost:5000/instrumentDB/getLatestValue'
        response = requests.get(url, params={'cute_name': self._name, 'label': quantity})
        if 300 > response.status_code <= 200:
            # success
            pass
        else:
            response.raise_for_status()

        value = response.json()
        if value['latest_value'] is None:
            return self.quantities[quantity]['def_value']
        else:
            return value['latest_value']

    def set_value(self, quantity, value):
        self._check_limits(quantity, value)
        url = r'http://localhost:5000/instrumentDB/setLatestValue'
        response = requests.put(url, params={'cute_name': self._name, 'label': quantity, 'latest_value': value})
        if 300 > response.status_code <= 200:
            # success
            pass
        else:
            response.raise_for_status()

    '''Closes Picoscope. Should be called when done using NonVisaInstrumentManager'''

    def close(self):
        self._ps.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _signal_generator(self):
        frequency = float(self.get_value('Frequency'))
        offset_voltage = float(self.get_value('Offset'))
        pk_to_pk = float(self.get_value('Amplitude'))
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


if __name__ == '__main__':
    pass
