@echo off

echo "This script will install virtualenv & setup a Python Virtual Enviroment -> venv"
pause

echo "Installing Python virtualenv"
python -m pip install --upgrade pip
pip install virtualenv

echo:
echo "Creating venv virtual enviroment in current directory..."

py -m venv venv
venv\Scripts\activate
