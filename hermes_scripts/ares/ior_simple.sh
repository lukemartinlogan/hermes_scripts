#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh "${HOME}/ior_out/hi.txt"

# Hermes
echo "HERMES TESTS BEGIN"
ior_write_hermes_posix_fpp "1" "16MB" "1m" "_pfs_ssd_nvme_ram"