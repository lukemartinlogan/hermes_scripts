#!/bin/bash

CACHED_ENV=$1
COMMAND=${@:2}

. ${CACHED_ENV}
${COMMAND}
