#!/bin/bash

cd $( dirname "${BASH_SOURCE[0]}" )

rm -r venv

virtualenv venv

source venv/bin/activate
export PYTHONPATH="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )/lib:${PYTHONPATH}"

pip install pyyaml

cd CWtrainer
make clean
make
cd -
