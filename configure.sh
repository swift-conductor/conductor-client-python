#!/usr/bin/env bash

# get script dir
script_dir=$( cd `dirname ${BASH_SOURCE[0]}` >/dev/null 2>&1 ; pwd -P )

echo "Python ..."

# Do not install Python if in Anaconda environment or we are on Docker container
if [[ -z "$CONDA_DEFAULT_ENV" && ! -f /.dockerenv ]]
then
    # install Python 3.11 if not installed
    pyenv install 3.11 --skip-existing

    # create .python-version
    pyenv local 3.11
    pyenv versions

    # use Python 3 from .python-version for local development
    eval "$(pyenv init -)"    
fi

# create virtual environment
python3 -m venv .venv

# activate virtual environment
source .venv/bin/activate

# upgrade pip
pip install --upgrade wheel
pip install --upgrade pip

# build tools
pip install --upgrade build twine

# install this as editable package
source version.sh
pip install --editable .

