import pyvisa
import requests
from Insrument.instrument_manager import InstrumentManager


class InstrumentConnectionService:
    def __init__(self) -> None:
        self._connected_instruments = {}

    def connect_to_visa_instrument(self, cute_name: str):
        """Creates and stores connection to given VISA instrument"""
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

        if connection_str is None:
            raise Exception(f"Could not connect to {cute_name}.")
        
        im = InstrumentManager(cute_name, connection_str)
        self._connected_instruments[cute_name] = im
        print(f"Connected to {cute_name}.")
    
    def disconnect_instrument(self, cute_name: str):
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
        

        
    
