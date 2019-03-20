#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Generates the content of a Makefile that'll count the number of free
# cores on all cluster nodes. Stores data as CSV files in
# ./free_core_data. The files will be named with the hostname of the
# cluster node.
# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Run with ./gen_core_counter_makefile.py > MakefileCoreCounter
# Run resulting makefile with make -f MakefileCoreCounter -j<number of clusters>

from cluster_specs import all_node_hostnames

print("SERVERS=\\")
for node_hostname in all_node_hostnames():
    print(f"{node_hostname}\\")

print("")

print("all: $(SERVERS)\n")

for node_hostname in all_node_hostnames():
    print("")
    print(f"{node_hostname}:")
    print(f"\t-ssh -oBatchMode=yes -oStrictHostKeyChecking=no {node_hostname} -t \"cd cs3243-poker-agent/cluster_runner; ./free_cpu_counter.py\" > free_core_data/{node_hostname}")
