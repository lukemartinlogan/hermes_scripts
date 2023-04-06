#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/local/ior.sh "release"

# IOR write with posix
ior_write_hermes_posix_fpp "1" "64GB" "1m" "_ram"
ior_write_hermes_posix_fpp "2" "32GB" "1m" "_ram"
ior_write_hermes_posix_fpp "4" "16GB" "1m" "_ram"
