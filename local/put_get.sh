#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/local/test_commands.sh "release"

test_api_bench "1" "putget" "4k" "1024"
#test_api_bench "2" "putget" "4k" "1024"
#test_api_bench "4" "putget" "4k" "1024"
#test_api_bench "8" "putget" "4k" "1024"

