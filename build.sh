#!/usr/bin/env bash

source configure.sh

rm -rf dist && python3 -m build
