#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/local/test_commands.sh "release"

# IOR write with posix
ior_write_hermes_posix_fpp "4" "4GB" "1m" "_ram"
