# InstrumentServer
Python Flask based server handling all communication between instruments &amp; clients

### VISA Backend:
Since PyVISA is used, you need to have a suitable VISA backend. PyVISA includes a backend that wraps the National Instruments’s VISA library. 
Download and install the NI-VISA library: [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#460225)

### Setup:
1. Run `setupEnv.bat`
2. Once in the virtual enviroment "venv", run `installPackages.bat`

### Run Instrument Server:
Starts on localhost (`127.0.0.1`) and port: `5000`. Threading enabled by default. <br> <br>
Just run: `__init__.py`

# Instrument Database
PostgresSQL database with parsed details from instrument driver.

## Containerized instance of Postgres Alpine:

Requires Docker to be installed on HOST system.

From DB directory, run:
```commandline
docker-compose up -d
```

### Connection details:
- Host: localhost  
- Port: 5432  
- Username: postgres  
- Password: 1234  
- Database name: instrument_db  

### Connect with Command Prompt:
Default schema: `public` <br>
`psql -h localhost -p 5432 -U postgres instrument_db`

---
##### Icon Attributions 
<a href="https://www.flaticon.com/free-icons/server" title="server icons">Server icons created by Pixel perfect - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/play-button" title="play button icons">Play button icons created by Roundicons - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/lab" title="lab icons">Lab icons created by surang - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/gear" title="gear icons">Gear icons created by Freepik - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/cancel" title="cancel icons">Cancel icons created by Freepik - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/plus" title="plus icons">Plus icons created by dmitri13 - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/create" title="create icons">Create icons created by Arkinasi - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/ui" title="ui icons">Ui icons created by icon wind - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/connect" title="connect icons">Connect icons created by Dreamstale - Flaticon</a>
<br>
<a href="https://www.flaticon.com/free-icons/disconnected" title="disconnected icons">Disconnected icons created by Alfian Dwi Hartanto - Flaticon</a>