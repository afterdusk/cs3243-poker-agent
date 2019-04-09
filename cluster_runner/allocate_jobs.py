#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates allocated_jobs.txt containing job allocations for each server.
# Run with python3 allocate_jobs.py.
# node_manage.sh uses the resulting file.

from math import floor
from re import findall
from cluster_specs import all_whitelisted_node_hostnames

def num_jobs_for_node(node_hostname):
    jerlim_pstree = None
    with open(f"free_core_data/{node_hostname}", 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return None
        num_cores = int(lines[-1])
        num_used_cores = int(lines[-2])
        if len(lines) > 2:
            jerlim_pstree = lines[-3]

    try:
        jerlim_num_jobs = [int(s) for s in findall(r'\d+', jerlim_pstree)][0]
    except:
        jerlim_num_jobs = 0
    num_free_cores = max(0, num_cores - num_used_cores)
    num_actual_free_cores = num_free_cores
    num_free_cores = min(num_cores, max(0, num_cores - num_used_cores + jerlim_num_jobs))  # Ignore Jeremy Lim's indiscriminate spamming

    # If server has too few cores, don't allocate jobs to it
    num_jobs = 0
    spite = False
    if num_free_cores < 3:
        num_jobs = 0
    # If server is basically idle, commandeer WITH SPITE
    elif num_free_cores > num_cores - 3:
        num_jobs = num_free_cores * 2
        spite = True
    # Otherwise only allocate num free cores - 2. Give chance
    else:
        num_jobs = num_free_cores - 2
    return (num_jobs, num_cores, num_free_cores, num_actual_free_cores, jerlim_num_jobs, spite)


if __name__ == "__main__":
    node_hostnames = all_whitelisted_node_hostnames()
    with open("allocated_jobs.txt", 'w') as f:
        # Stats for convenience
        total_jobs = 0
        total_jerlim_jobs = 0
        total_actual_free_cores = 0
        total_free_cores = 0
        total_cores = 0

        for node_hostname in node_hostnames:
            job_and_core_stats = num_jobs_for_node(node_hostname)
            if job_and_core_stats is None:
                num_jobs = 0
                print(f"{node_hostname} uncontactable.")
            else:
                num_jobs, num_cores, num_free_cores, num_actual_free_cores, jerlim_num_jobs, spite = job_and_core_stats
                total_jobs += num_jobs
                total_jerlim_jobs += jerlim_num_jobs
                total_actual_free_cores += num_actual_free_cores
                total_free_cores += num_free_cores
                total_cores += num_cores
                print("{:2d} jobs on {:2d}+{:2d}/{:2d}/{:2d} free cores on {}{}.".format(num_jobs, num_actual_free_cores, jerlim_num_jobs, num_free_cores, num_cores, node_hostname, " WITH SPITE" if spite else ""))

            # Ignore all full/uncontactable servers
            if num_jobs > 0:
                f.write(f"{node_hostname}\n{num_jobs}\n")

    print(f"Allocated {total_jobs} jobs on {total_actual_free_cores}/{total_free_cores}/{total_cores} free cores on {len(node_hostnames)} nodes.")
