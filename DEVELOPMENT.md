# Development

You need Python 3.8+

## Configure project

This creates virtual environment and installs all packages from `setup.cfg`

```sh
source configure.sh
```

## Test

### Start Conductor server

See [Running Conductor from source](https://swiftconductor.com/getting-started/running/source.html)

### Run integration tests

```sh
source configure.sh

export CONDUCTOR_SERVER_URL=http://localhost:8080/api

python ./tests/integration/main.py --clients-only
python ./tests/integration/main.py --workflow-execution-only
```

## Update version

Change the version in `version.sh` or set `CONDUCTOR_PYTHON_VERSION` environment variable.

NOTE: `version.sh` is sourced from the `configure.sh` script.