#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh "${HOME}/ior_out/hi.txt"

# Basline
ior_write_read_posix_fpp "1" "8GB" "1m" "_ram"

# Hermes
ior_write_read_hermes_posix_fpp "1" "8GB" "1m" "_ram"
