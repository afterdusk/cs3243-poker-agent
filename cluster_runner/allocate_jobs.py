#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates allocated_jobs.txt containing job allocations for each server.
# Run with python3 allocate_jobs.py.
# node_manage.sh uses the resulting file.

from math import floor
from cluster_specs import all_whitelisted_node_hostnames

def num_jobs_for_node(node_hostname):
    with open(f"free_core_data/{node_hostname}", 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return None
        num_cores = int(lines[-1])
        num_free_cores = int(lines[-2])

    # If server has too few cores, don't allocate jobs to it
    num_jobs = 0
    if num_free_cores < 3:
        num_jobs = 0
    # If server is basically idle, commandeer
    elif num_free_cores > num_cores - 6:
        num_jobs = num_free_cores
    # Otherwise only allocate num free cores - 2. Give chance
    else:
        num_jobs = num_free_cores - 2
    return (num_jobs, num_free_cores, num_cores)


if __name__ == "__main__":
    node_hostnames = all_whitelisted_node_hostnames()
    with open("allocated_jobs.txt", 'w') as f:
        # Stats for convenience
        total_jobs = 0
        total_free_cores = 0
        total_cores = 0

        for node_hostname in node_hostnames:
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

            # Ignore all full/uncontactable servers
            if num_jobs > 0:
                f.write(f"{node_hostname}\n{num_jobs}\n")

    print(f"Allocated {total_jobs} jobs on {total_free_cores}/{total_cores} free cores on {len(node_hostnames)} nodes.")
