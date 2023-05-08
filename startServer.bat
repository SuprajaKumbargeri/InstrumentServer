@echo off

Rem This script starts Instrument Server - can just be clicked
echo "Starting Instrument Server"
timeout 2

CALL pythonPath.bat %cd% InstrumentServer/__init__.py
