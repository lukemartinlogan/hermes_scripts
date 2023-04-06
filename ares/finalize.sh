#!/bin/bash
spack load --only dependencies hermes

HERMES_SCRIPTS_ROOT=`pwd`
. ${HERMES_SCRIPTS_ROOT}/ares/hermes_paths.sh

mkdir /tmp/test_hermes

export HERMES_CLIENT_CONF=${HERMES_SCRIPTS_ROOT}/local/conf/hermes_client.yaml
export HERMES_CONF=${HERMES_SCRIPTS_ROOT}/local/conf/hermes_server.yaml

# Start daemon
echo "STARTING DAEMON"
${CMAKE_BINARY_DIR}/bin/hermes_daemon &
sleep 3
echo "DAEMON STARTED"

# Finalize Hermes
${CMAKE_BINARY_DIR}/bin/finalize_hermes
