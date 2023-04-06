#!/bin/bash
spack load --only dependencies hermes
spack load ior

# Load the paths
HERMES_SCRIPTS_ROOT=`pwd`
HERMES_BUILD_TYPE=$1
. ${HERMES_SCRIPTS_ROOT}/local/hermes_${HERMES_BUILD_TYPE}_paths.sh
echo "${CMAKE_SOURCE_DIR}"

mkdir /tmp/test_hermes

# A write-only workload to new files with POSIX
ior_write_posix_fpp() {
  NPROCS=$1
  IO_SIZE_PER_RANK=$2
  TRANSFER_SIZE=$3

  # Run IOR
  echo "STARTING IOR"
  echo "ior -w -o /tmp/test_hermes/hi.txt -t "${TRANSFER_SIZE}" -b "${IO_SIZE_PER_RANK}" -F"
  mpirun -n "${NPROCS}" \
  -genv PATH="${PATH}" \
  -genv LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" \
  ior -w -o /tmp/test_hermes/hi.txt -t "${TRANSFER_SIZE}" -b "${IO_SIZE_PER_RANK}" -F

  echo "FINISHED IOR"

  # Cleanup
  rm -rf /tmp/test_hermes/*
  rm -rf ${HOME}/test/*
}

# A write-only workload to new files with POSIX
ior_write_hermes_posix_fpp() {
  NPROCS=$1
  IO_SIZE_PER_RANK=$2
  TRANSFER_SIZE=$3
  CONF_SUFFIX=$4
  export HERMES_CLIENT_CONF=${HERMES_SCRIPTS_ROOT}/local/conf/hermes_client.yaml
  export HERMES_CONF=${HERMES_SCRIPTS_ROOT}/local/conf/hermes_server${CONF_SUFFIX}.yaml

  # Start daemon
  echo "STARTING DAEMON"
  ${CMAKE_BINARY_DIR}/bin/hermes_daemon &
  sleep 3
  echo "DAEMON STARTED"

  # Run IOR
  echo "STARTING IOR"
  echo "ior -w -o /tmp/test_hermes/hi.txt -t "${TRANSFER_SIZE}" -b "${IO_SIZE_PER_RANK}" -F"
  mpirun -n "${NPROCS}" \
  -genv PATH="${PATH}" \
  -genv LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" \
  -genv LD_PRELOAD="${CMAKE_BINARY_DIR}/bin/libhermes_posix.so" \
  -genv HERMES_CLIENT_CONF="${HERMES_CLIENT_CONF}" \
  -genv HERMES_CONF="${HERMES_CONF}" \
  -genv HERMES_ADAPTER_MODE=kScratch \
  ior -w -o /tmp/test_hermes/hi.txt -t "${TRANSFER_SIZE}" -b "${IO_SIZE_PER_RANK}" -F

  echo "FINISHED IOR"

  # Finalize Hermes
  ${CMAKE_BINARY_DIR}/bin/finalize_hermes

  # Cleanup
  rm -rf /tmp/test_hermes/*
  rm -rf ${HOME}/test/*
}
