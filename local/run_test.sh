#!/bin/bash

spack load --only dependencies hermes
spack load ior

# NOTE: this script assumes you are cd'd into hermes_scripts
TEST_NAME=$1
python3 local/test_manager.py "${TEST_NAME}"
