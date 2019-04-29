#!/bin/bash
echo "NodeMICMAC by DroneMapper.com"

RUNPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$RUNPATH/run.py "$@"
exit 0