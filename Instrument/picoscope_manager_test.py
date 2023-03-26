from picoscope_manager import PicoscopeManager
import requests
import sys
import importlib

name = "Picoscope 6000"

url = r'http://127.0.0.1:5000/instrumentDB/getInstrument'
response = requests.get(url, params={'cute_name': name})
driver = dict(response.json())

driver = driver["general_settings"]["driver_path"]
sys.path.append(driver)
my_module = importlib.import_module("Koo")


ps6000 = getattr(my_module, "Driver")(name=name, driver=driver)

try:
    print(ps6000.get_value('Frequency'))
    # print(ps6000.get_value('Offset'))
    # print(ps6000.get_value('Amplitude'))
    # print(ps6000.get_value('Wave Type'))
    #
    # ps6000.set_value('Frequency', 1000)
    # ps6000.set_value('Offset', 0)
    # ps6000.set_value('Amplitude', 4)
    # ps6000.set_value('Wave Type', "Sine")
    #
    # print("----------------------------")
    # print(ps6000.get_value('Frequency'))
    # print(ps6000.get_value('Offset'))
    # print(ps6000.get_value('Amplitude'))
    # print(ps6000.get_value('Wave Type'))

    # result = ps6000._signal_generator()
    # print(result)

except Exception as e:
    print(e)
finally:
    pass
