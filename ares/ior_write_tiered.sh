#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh "${HOME}/test_hermes/hi.txt"

# HERMES
echo "HERMES TESTS BEGIN"
ior_write_posix_fpp "40" "4GB" "1m"
ior_write_hermes_posix_fpp "40" "4GB" "1m" "_pfs_ssd"
ior_write_hermes_posix_fpp "40" "4GB" "1m" "_pfs_ssd_nvme"
ior_write_hermes_posix_fpp "40" "4GB" "1m" "_pfs_ssd_nvme_ram"
