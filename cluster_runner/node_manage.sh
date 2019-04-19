#!/bin/bash
# Script to be run on the server/admin/controlling node

if [ $# -lt 1 ]
then
    echo "Usage: ./node_manage.sh <countcpu|start|kill>"
    exit 1
fi

if [ "$1" = "countcpu" ]; then
    # Count cores
    python3 cluster_specs.py hostnames | parallel -j300 -u "ssh -oBatchMode=yes -oStrictHostKeyChecking=no {} -t \"cd cs3243-poker-agent/cluster_runner; python3 free_cpu_counter.py\" > free_core_data/{}"

    # Generate job allocations from gathered data
    python3 allocate_jobs.py

elif [ "$1" = "start" ]; then
    # Start jobs on server
    cat allocated_jobs.txt | parallel -n2 -j300 -u "ssh -oBatchMode=yes -oStrictHostKeyChecking=no {1} -t \"cd cs3243-poker-agent/cluster_runner; ./node_run.sh {2} > /dev/null\""

elif [ "$1" = "kill" ]; then
    # Killall jobs on server
    python3 cluster_specs.py whitelistedhostnames | parallel -j300 -u "ssh -oBatchMode=yes -oStrictHostKeyChecking=no {} -t \"killall python mosquitto\""

fi
