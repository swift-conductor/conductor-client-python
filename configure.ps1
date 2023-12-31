# Python
Write-Output "Python ..."

# create virtual environment
C:\tools\python3\python.exe -m venv .venv

# activate virtual environment
.venv\Scripts\Activate.ps1

# upgrade pip
python -m pip install --upgrade pip

# install this as editable package
pip install --editable .
