#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`
CMAKE_SOURCE_DIR=${MY_PROJECTS}/hermes
cd ${CMAKE_SOURCE_DIR}/cmake-build-debug-gcc-no-sanitize
CMAKE_BINARY_DIR=`pwd`
HERMES_TRAIT_PATH=${CMAKE_BINARY_DIR}/bin