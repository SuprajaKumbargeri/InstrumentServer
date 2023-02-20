# InstrumentServer
Python Flask based server handling all communication between instruments &amp; clients

### VISA Backend:
Since PyVISA is used, you need to have a suitable VISA backend. PyVISA includes a backend that wraps the National Instruments’s VISA library. 
Download and install the NI-VISA library: [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#460225)

### Setup
1. Run `setupEnv.bat`
2. Once in the virtual enviroment "venv", run `installPackages.bat`

### Run
`flask --app InstrumentServer run --with-threads`

### Run with debugging (avoid for now)
`flask --app InstrumentServer --debug run`

# Instrument Database
PostgreSQL database with parsed details from instrument driver

### Connection details
- Host: localhost  
- Port: 5432  
- Username: postgres  
- Password: 1234  
- Database name: instrument_db  

### Connect with Command Prompt
`psql -h localhost -p 5432 -U postgres instrument_db`
