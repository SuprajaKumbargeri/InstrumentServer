from picoscope_manager import PicoscopeManager
from InstrumentServer.instrument_connection_service import *

'''
add picoscope instrument to the db
'''
# details = {"cute_name": "Picoscope 6000",
#            "interface": "USB",
#            "ip_address": "N/A",
#            "serial": "False",
#            "visa": "False",
#            "path": r'C:\GitHub\jkoo\InstrumentServer\Picoscope_6000.ini'
#            }
#
# connect_result, msg = add_instrument_to_database(details)
# print(connect_result)
# print(msg)

'''
simulate connect_to_visa_instrument

will create connect_to_visa_instrument to handle picoscope

'''

cute_name = "Picoscope 6000"
url = r'http://localhost:5000/instrumentDB/getInstrument'
response = requests.get(url, params={'cute_name': cute_name})

if 300 > response.status_code <= 200:
    # success
    print("getInsturment success!")
    pass
else:
    response.raise_for_status()

response_dict = dict(response.json())
ps6000 = PicoscopeManager(cute_name, response_dict)

try:
    print(ps6000.get_value('Frequency'))
    ps6000.set_value('Frequency', 2000)
    print(ps6000.get_value('Frequency'))

except Exception as e:
    print(e)
finally:
    ps6000._close()

