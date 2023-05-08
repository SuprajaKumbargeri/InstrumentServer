@ECHO OFF

Rem This script uses Python in "venv" virtual environment and sets PYTHONPATH var
setlocal
set PYTHONPATH=%1
venv\Scripts\python.exe %2 %3
endlocal
