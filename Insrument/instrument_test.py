from Instrument import InstrumentManager

driver = 'C:\\Users\\stst5991\\Desktop\\Code\\Agilent_33220A_WaveformGenerator\\Agilent_33220A_WaveformGenerator.ini'
instr = InstrumentManager(driver, 'GPIB0::13::INSTR')
try:
    print(instr['Frequency'])
except Exception as e:
    print(e)
finally:
    instr.close()
