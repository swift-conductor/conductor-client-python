#!/usr/bin/env bash

source configiure.sh

python3 -m twine upload --skip-existing dist/*