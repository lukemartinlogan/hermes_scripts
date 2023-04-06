#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`
CMAKE_SOURCE_DIR=${MY_PROJECTS}/hermes
cd ${CMAKE_SOURCE_DIR}/build
CMAKE_BINARY_DIR=`pwd`
HERMES_TRAIT_PATH=${CMAKE_BINARY_DIR}/bin

mkdir /mnt/nvme/llogan/test_hermes
mkdir /mnt/ssd/llogan/test_hermes
mkdir ${HOME}/test_hermes
