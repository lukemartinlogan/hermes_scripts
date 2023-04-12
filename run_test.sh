#!/bin/bash

spack load --only dependencies hermes
spack load ior

# NOTE: this script assumes you are cd'd into hermes_scripts
TEST_MACHINE=$1
TEST_NAME=$2
python3 "bin/run_test" "${TEST_MACHINE}" "${TEST_NAME}"
