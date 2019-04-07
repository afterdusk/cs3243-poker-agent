#!/bin/bash

# Script to be run on a client node
# Usage: ./node_run.sh <num parallel client jobs>
# E.g. ./node_run.sh 20

if [ $# -lt 1 ]
then
    echo "Usage: ./node_run.sh <num parallel client jobs>"
    exit 1
fi

# Cleanup if required
function finish {
    killall mosquitto
}
trap finish EXIT

export TMPDIR=/temp/e-liang/nodetmp
mkdir -p $TMPDIR || unset TMPDIR

~/.linuxbrew/sbin/mosquitto -c mosquitto_client_cluster_broker.conf &

sleep 5

pushd ..
seq $1 | parallel -u python CLIENT_script.py
popd
