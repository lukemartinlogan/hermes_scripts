#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`
CMAKE_SOURCE_DIR=${HOME}/hermes
cd ${CMAKE_SOURCE_DIR}/build
CMAKE_BINARY_DIR=`pwd`
HERMES_TRAIT_PATH=${CMAKE_BINARY_DIR}/bin

mkdir /mnt/nvme/${USER}/test_hermes
mkdir /mnt/ssd/${USER}/test_hermes
mkdir ${HOME}/test_hermes
mkdir /mnt/ssd/${USER}/ior_out
mkdir ${HOME}/ior_out

cleanup_hermes() {
  rm -rf /mnt/nvme/${USER}/test_hermes/*
  rm -rf /mnt/ssd/${USER}/test_hermes/*
  rm -rf /mnt/ssd/${USER}/ior_out/*
  rm -rf ${HOME}/test_hermes/*
  rm -rf ${HOME}/ior_out/*
}