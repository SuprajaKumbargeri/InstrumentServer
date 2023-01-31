from instrument_manager import InstrumentManager

driver = r'C:\Users\stst5991\Desktop\Code\DSinstr_SG12000PRO_SignalGenerator\DSinstr_SG12000PRO_SignalGenerator.ini'
instr = InstrumentManager(driver, 'GPIB0::13::INSTR')
try:
    print(instr.get_value('Power'))
except Exception as e:
    print(e)
finally:
    instr.close()
