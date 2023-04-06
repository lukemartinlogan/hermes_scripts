#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh

# Hermes
echo "HERMES TESTS BEGIN"
ior_write_hermes_posix_fpp "10" "10GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "20" "5GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "30" "2.5GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "40" "1.25GB" "1m" "_pfs_ssd_nvme_ram"
