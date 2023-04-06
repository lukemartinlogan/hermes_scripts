#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/local/ior.sh "dbg"

# IOR write with posix
ior_write_hermes_posix_fpp "8" "1GB" "1m" "_ram"
