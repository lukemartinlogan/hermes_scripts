#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh

# HERMES
echo "HERMES TESTS BEGIN"
ior_write_hermes_posix_fpp "40" "16GB" "1m" "_pfs"
ior_write_hermes_posix_fpp "40" "16GB" "1m" "_pfs_ssd"
ior_write_hermes_posix_fpp "40" "16GB" "1m" "_pfs_ssd_nvme"
ior_write_hermes_posix_fpp "40" "16GB" "1m" "_pfs_ssd_nvme_ram"
