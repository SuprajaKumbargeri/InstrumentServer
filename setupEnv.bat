@echo off

echo "This script will install virtualenv & setup a Python Virtual Environment -> venv"
pause

echo "Installing Python virtualenv"
echo "Checking for pip updates..."
py -m pip install --upgrade pip
pip install virtualenv

echo:
echo "Creating venv virtual environment in current directory..."

py -m venv venv
venv\Scripts\activate
