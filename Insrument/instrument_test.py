from instrument_manager import InstrumentManager

driver = r'C:\Users\stst5991\Desktop\Code\Agilent_33220A_WaveformGenerator\Agilent_33220A_WaveformGenerator.ini'
instr = InstrumentManager(driver, 'USB0::0x0957::0x0407::SG44001573::INSTR')
try:
    print(instr.get_value('Frequency'))
    instr.set_value('Frequency', 1000)
    print(instr.get_value('Frequency'))
except Exception as e:
    print(e)
finally:
    instr.close()
