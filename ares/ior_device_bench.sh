#!/bin/bash

HERMES_SCRIPTS_ROOT=`pwd`

# Hermes
echo "HERMES TESTS BEGIN"
. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh "/mnt/nvme/${USER}/test_hermes"
ior_write_posix_fpp "2" "80GB" "1m"
ior_write_posix_fpp "4" "40GB" "1m"
ior_write_posix_fpp "8" "20GB" "1m"

. ${HERMES_SCRIPTS_ROOT}/ares/ior.sh "/mnt/ssd/${USER}/test_hermes"
ior_write_posix_fpp "2" "80GB" "1m"
ior_write_posix_fpp "4" "40GB" "1m"
ior_write_posix_fpp "8" "20GB" "1m"