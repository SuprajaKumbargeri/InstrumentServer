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

class InstrumentConnectionService:
    def __init__(self) -> None:
        self._connected_instruments = {}
    def connect_to_visa_instrument(self, cute_name: str):
        """Creates and stores connection to given VISA instrument"""

        if cute_name in self._connected_instruments.keys():
            raise ValueError(f'{cute_name} is already connected.')

        # Use cute_name to determine the interface (hit endpoint for that)
        url = r'http://127.0.0.1:5000/instrumentDB/getInstrument'
        response = requests.get(url, params={'cute_name': cute_name})

        # raise exception for error
        if 200 < response.status_code >= 300:
            response.raise_for_status()

        response_dict = dict(response.json())
        interface = response_dict['instrument_interface']['interface']

        # Might be None
        ip_address = response_dict['instrument_interface']['ip_address']
        print('Cute_name {} uses interface: {}'.format(cute_name, interface))

        # Get list of resources to compare to
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        connection_str = None

        if interface == INST_INTERFACE.TCPIP.name:
            print('TCPIP instrument IP address is {}'.format(ip_address))
            connection_str = self.make_conn_str_tcip_instrument(ip_address)
        else:
            # Get the connection string (used to get PyVISA resource)
            for resource in resources:
                if interface in resource:
                    connection_str = resource
                    break

        if connection_str is None:
            raise ConnectionError(f"Could not connect to {cute_name}. Unable to find valid connection string.")

        # Connect to instrument
        print('Using connection string: {} to connect to {}'.format(connection_str, cute_name))
        try:
            im = InstrumentManager(cute_name, connection_str)
            self._connected_instruments[cute_name] = im
            print(f"Connected to {cute_name}.")
        # InstrumentManager may throw value error, this service should throw a Connection error
        except ValueError as e:
            raise ConnectionError(e)

    def disconnect_instrument(self, cute_name: str):
        if cute_name not in self._connected_instruments.keys():
            raise KeyError(f"{cute_name} is not currently connected.")

        del self._connected_instruments[cute_name]
        print(f"Disnonnected {cute_name}.")

    def disconnect_all_instruments(self):
        instr_names = list(self._connected_instruments.keys())
        list_of_failures = ()

        for instrument_name in instr_names:
            try:
                self.disconnect_instrument(instrument_name)
            except:
                list_of_failures

        if len(list_of_failures) > 0:
            raise Exception(f"Failed to disconnect from the following instruments: {list_of_failures}")


    def make_conn_str_tcip_instrument(self, ip_address: str) -> str:
        """
        Construct a connection string for TCPIP instruments
        Example: TCPIP0::192.168.0.7::INSTR
        """
        # Default TCPIP Interface
        TCPIP_INTERFACE = 'TCPIP0'
        END = 'INSTR'

        return '{}::{}::{}'.format(TCPIP_INTERFACE, ip_address, END)
    
