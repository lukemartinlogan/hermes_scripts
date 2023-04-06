#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh

# Hermes
echo "HERMES TESTS BEGIN"
ior_write_hermes_posix_fpp "2" "80GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "4" "40GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "5" "32GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "10" "16GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "20" "8GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "30" "5GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "40" "4GB" "1m" "_pfs_ssd_nvme_ram"
