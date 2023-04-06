#!/bin/bash
HERMES_SCRIPTS_ROOT=`pwd`
CMAKE_SOURCE_DIR=${HOME}/hermes
cd ${CMAKE_SOURCE_DIR}/build
CMAKE_BINARY_DIR=`pwd`
HERMES_TRAIT_PATH=${CMAKE_BINARY_DIR}/bin

mkdir /mnt/nvme/llogan/test_hermes
mkdir /mnt/ssd/llogan/test_hermes
mkdir ${HOME}/test_hermes
mkdir /mnt/ssd/llogan/ior_out
mkdir ${HOME}/ior_out

cleanup_hermes() {
  rm -rf /mnt/nvme/llogan/test_hermes/*
  rm -rf /mnt/ssd/llogan/test_hermes/*
  rm -rf /mnt/ssd/llogan/ior_out/*
  rm -rf ${HOME}/test_hermes/*
  rm -rf ${HOME}/ior_out/*
}