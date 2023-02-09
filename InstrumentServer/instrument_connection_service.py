import pyvisa
import requests
from Insrument.instrument_manager import InstrumentManager


def connect_to_visa_instrument(cute_name: str):
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    interface = None
    connection_str = None

    # Use cute_name to determine the interface (hit endpoint for that)

    url = r'http://localhost:5000/instrumentDB/getInstrument'
    response = requests.get(url, params={'cute_name': cute_name})

    if 300 > response.status_code <= 200:
        # success
        pass
    else:
        response.raise_for_status()

    response_dict = dict(response.json())
    interface = response_dict['instrument_interface']['interface']
    print('Cute_name {} uses interface {}'.format(cute_name, interface))

    # Get the connection string (used to get PyVISA resource)
    for resource in resources:
        if interface in resource:
            connection_str = resource
            print('Using connection string: {} to connect to {}'.format(connection_str, cute_name))
            break


    try:
        im = InstrumentManager(cute_name, connection_str)
        print(im.name)
    except Exception as e:
        print(e)
        return False, e
    

    im.close()

    return True, None


    



