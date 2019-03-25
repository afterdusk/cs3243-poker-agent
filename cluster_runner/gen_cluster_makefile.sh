#!/bin/bash

# Count cores
python3 cluster_specs.py hostnames | parallel -j300 -u "ssh -oBatchMode=yes -oStrictHostKeyChecking=no {} -t \"cd cs3243-poker-agent/cluster_runner; python3 free_cpu_counter.py\" > free_core_data/{}"

# Make MakefileCluster from gathered data
python3 clustermakefilegen.py
