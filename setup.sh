#!/bin/bash

# Script root directory.
puppy_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the PYTHONPATH For python module(s).
python_dir=$puppy_dir/lib
[[ "$PYTHONPATH" =~ "${python_dir}" ]] || export PYTHONPATH=${python_dir}:$PYTHONPATH
