import logging
from pyvisa import *
import ctypes
from picoscope import *
from .. InstrumentDetection.instrument_resource import *
import time
import matplotlib.pyplot as plt
import numpy as np
class InstrumentComService:

    def __init__(self, logger: logging.Logger, visa_inst_list: InstrumentResource , pico_int_list: InstrumentResource):
        self.logger = logger
        self.visa_instrument_resources = visa_inst_list
        self.pico_instruments = pico_int_list

    def close_all_instruments(self):
        logger.info("Closing all connections to known Instruments...")

        for inst in self.visa_instrument_resources:
            logger.info("Closing {}".format(inst.get_model()))
            driver = inst.get_driver()
            driver.close()

        for inst in self.pico_instruments:
            logger.info("Closing {}".format(inst.get_model()))
            driver = inst.get_driver()
            driver.close()

    def handle_ask(self, instrument: str, cmd: str, type: INST_TYPE):

        logger.info("handle_ask() - instrument: " + instrument + " cmd: " + cmd)

        if type == INST_TYPE.VISA:
            for instrument_resource in self.visa_instrument_resources:
                if instrument_resource.get_model() == instrument.upper():
                    driver = instrument_resource.get_driver()

                    try:
                        self.logger.info(f"Querying: {cmd}")
                        response = driver.query(cmd)
                        self.logger.info(f"Response: {response}")
                        return response

                    except Exception as e:
                        inst = repr(self)
                        e.args = e.args + ("asking " + repr(cmd) + " to " + inst,)
                        return 500  

        elif type == INST_TYPE.PICO:
            for instrument_resource in self.pico_instruments:
                if instrument_resource.get_model() == instrument.upper():
                    driver = instrument_resource.get_driver()
                    #Open Pico Instrument Asynchronously
                    # driver.openUnitAsync(serialNumber='AR571/017')#(serialNumber=None)
                    try:
                        self.logger.info(f"Querying: {cmd}")
                        cmd = cmd.split(" ")
                        command = cmd[0]

                        if command == "signal_generator":
                            # waveform_desired_duration = 1E-3
                            waveform_desired_duration = float(cmd[1])
                            offsetVoltage = float(cmd[2])
                            pkToPk = float(cmd[3])
                            waveType = cmd[4]
                            obs_duration = 10 * waveform_desired_duration
                            sampling_interval = obs_duration / 4096

                            (actualSamplingInterval, nSamples, maxSamples) = driver.setSamplingInterval(
                                sampling_interval, obs_duration)
                            print("Sampling interval = %f ns" % (actualSamplingInterval * 1E9))
                            print("Taking  samples = %d" % nSamples)
                            print("Maximum samples = %d" % maxSamples)

                            driver.setChannel('A', 'DC', 2.0, 0.0, True, False)
                            driver.setSimpleTrigger('A', 0.0, 'Rising', delay=0, timeout_ms=100,
                                                enabled=True)

                            driver.setSigGenBuiltInSimple(offsetVoltage=offsetVoltage, pkToPk=pkToPk, waveType=waveType,
                                                      frequency=1 / waveform_desired_duration,
                                                      shots=1, triggerType="Rising",
                                                      triggerSource="None")

                            # take the desired waveform
                            # This measures all the channels that have been enabled

                            driver.runBlock()
                            driver.waitReady()
                            print("Done waiting for trigger")
                            time.sleep(10)
                            driver.runBlock()
                            driver.waitReady()

                            response = dataA = driver.getDataV('A', nSamples, returnOverflow=False)
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

                    except Exception as e:
                        self.logger.info("error message: " + str(e))
                        inst = repr(self)
                        e.args = e.args + ("asking " + repr(cmd) + " to " + inst,)
                        return 500


            #logging.info("Pico not yet implemented!")

        return 404

        
