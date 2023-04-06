#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh

# IOR write + read (no hermes)
# ior_write_read_posix_fpp "1" "8GB" "1m"

ior_write_read_hermes_posix_fpp "1" "8GB" "1m" "_ram"
