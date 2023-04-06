#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`

. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh

# IOR write with posix
ior_write_hermes_posix_fpp "10" "64GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "20" "32GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "30" "21GB" "1m" "_pfs_ssd_nvme_ram"
ior_write_hermes_posix_fpp "40" "16GB" "1m" "_pfs_ssd_nvme_ram"
