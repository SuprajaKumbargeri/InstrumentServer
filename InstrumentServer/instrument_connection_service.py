import pyvisa
import requests
import time
from enum import Enum
from Insrument.instrument_manager import InstrumentManager

class INST_INTERFACE(Enum):
    USB = 'USB'
    GPIB = 'GPIB'
    TCPIP = 'TCPIP'
    SERIAL = 'SERIAL'

def connect_to_visa_instrument(cute_name: str):
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    interface = None
    connection_str = None

    # Use cute_name to determine the interface (hit endpoint for that)

    url = r'http://127.0.0.1:5000/instrumentDB/getInstrument'
    response = requests.get(url, params={'cute_name': cute_name})

    if 300 > response.status_code <= 200:
        # success
        pass
    else:
        response.raise_for_status()

    response_dict = dict(response.json())
    interface = response_dict['instrument_interface']['interface']

    # Might be None
    ip_address = response_dict['instrument_interface']['ip_address']

    print('Cute_name {} uses interface: {}'.format(cute_name, interface))

    connection_str = ''
    if interface == INST_INTERFACE.TCPIP.name:
        print('TCPIP instrument IP address is {}'.format(ip_address))
        connection_str = make_conn_str_tcip_instrument(ip_address)
    else:
        # Get the connection string (used to get PyVISA resource)
        for resource in resources:
            if interface in resource:
                connection_str = resource
                break

    print('Using connection string: {} to connect to {}'.format(connection_str, cute_name))

    try:
        im = InstrumentManager(cute_name, connection_str)
        print(im.name)
    except Exception as e:
        print(e)
        return False, e

    im.close()

    return True, None


def make_conn_str_tcip_instrument(ip_address: str) -> str:
    '''
    Example: TCPIP0::192.168.0.7::INSTR 
    '''
    # Default TCPIP Interface
    TCPIP_INTERFACE = 'TCPIP0'
    END = 'INSTR'

    return '{}::{}::{}'.format(TCPIP_INTERFACE, ip_address, END)
    
