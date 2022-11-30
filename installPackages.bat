@echo off
echo "Installing all required Python packages for Instrument Server..."
echo:

python -m pip install --upgrade pip
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt