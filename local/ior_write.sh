#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/local/ior.sh "release"

# IOR write with posix
ior_write_hermes_posix_fpp "1" "6GB" "1m" "_ram"
