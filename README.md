# InstrumentServer
Python Flask based server handling all communication between instruments &amp; clients

### Setup
1. Run `setupEnv.bat`
2. Once in the virtual enviroment "venv", run `installPackages.bat`

### Run
`flask --app InstrumentServer run`

### Run with debugging (avoid for now)
`flask --app InstrumentServer --debug run`

# Instrument Database
PostgreSQL database with parsed details from instrument driver

### Connection details
Host: localhost  
Port: 5432  
Username: postgres  
Password: 1234  
Database name: instrument_db  

### Connect with Command Prompt
`psql -h localhost -p 5432 -U postgres instrument_db`
