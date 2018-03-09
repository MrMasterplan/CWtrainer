#!/bin/bash

if [ x$CWdevshell == x'' ]
then
    echo spawning
    export CWdevshell=hello
    cd $(dirname $(readlink -m $BASH_SOURCE))
    bash --rcfile $BASH_SOURCE
    exit
fi

source ~/.bashrc
source venv/bin/activate
export PYTHONPATH="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )/lib:${PYTHONPATH}"



