from picoscope_manager import PicoscopeManager

driver = r'C:\Users\Picoscope_6000.ini'
instr = PicoscopeManager(driver)
try:
    print(instr.get_value('Frequency'))
    instr.set_value('Frequency', 1000)
    print(instr.get_value('Frequency'))
except Exception as e:
    print(e)
finally:
    instr.close()
