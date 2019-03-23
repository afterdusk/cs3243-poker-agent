#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates MakefileCluster, a Makefile that'll spawn clients on some servers
# Run with python3 clustermakefilegen.py
# Run resulting makefile with make -f MakefileCluster -j<number of clusters>

from math import floor
from cluster_specs import all_node_hostnames, node_name_to_hostname

blacklist_node_names = [
    "xcna1",  # Manually manage the server's server
    "xcnd32",  # Si Jie's group is training here
]

blacklist = [node_name_to_hostname(n) for n in blacklist_node_names]

def num_jobs_for_node(node_hostname):
    with open(f"free_core_data/{node_hostname}", 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return None
        num_cores = int(lines[-1])
        num_free_cores = int(lines[-2])

    # If server has too few cores, don't allocate jobs to it
    num_jobs = 0
    if num_free_cores < 6:
        num_jobs = 0
    # If server is basically idle, commandeer
    elif num_free_cores > num_cores - 4:
        num_jobs = num_free_cores
    # Otherwise only allocate 80% of cores, up to a limit
    else:
        num_jobs = min(floor(num_cores * 0.8), num_free_cores - 4)
    return (num_jobs, num_free_cores, num_cores)


if __name__ == "__main__":
    node_hostnames = all_node_hostnames()
    with open("MakefileCluster", 'w') as f:
        f.write("SERVERS=\\\n")
        for node_hostname in node_hostnames:
            if node_hostname in blacklist:
                continue
            f.write(f"{node_hostname}\\\n")
        f.write("\n")

        f.write("KILLSERVERS=\\\n")
        for node_hostname in node_hostnames:
            f.write(f"kill.{node_hostname}\\\n")
        f.write("\n")

        f.write("all: $(SERVERS)\n\n")
        f.write("killall: $(KILLSERVERS)\n\n")

        # Stats for convenience
        total_jobs = 0
        total_free_cores = 0
        total_cores = 0

        for node_hostname in node_hostnames:
            f.write("\n")

            f.write(f"kill.{node_hostname}:\n")
            f.write(f"\t-ssh -oBatchMode=yes -oStrictHostKeyChecking=no {node_hostname} -t \"killall python mosquitto\"\n")

            if node_hostname in blacklist:
                continue

            job_and_core_stats = num_jobs_for_node(node_hostname)
            if job_and_core_stats is None:
                num_jobs = 0
                print(f"{node_hostname} uncontactable.")
            else:
                num_jobs, num_free_cores, num_cores = job_and_core_stats
                total_jobs += num_jobs
                total_free_cores += num_free_cores
                total_cores += num_cores
                print("{:2d} jobs on {:2d}/{:2d} free cores on {}.".format(num_jobs, num_free_cores, num_cores, node_hostname))

            if num_jobs == 0:
                # Print empty recipe for full/uncontactable servers
                f.write(f"{node_hostname}: ;\n")
            else:
                f.write(f"{node_hostname}:\n")
                # Add 1 to num_jobs for broker
                f.write(f"\t-ssh -oBatchMode=yes -oStrictHostKeyChecking=no {node_hostname} -t \"cd cs3243-poker-agent; bash -cl 'make -j{num_jobs+1} > /dev/null'\"\n")
    
    print(f"Allocated {total_jobs} jobs on {total_free_cores}/{total_cores} free cores on {len(node_hostnames)} nodes.")
