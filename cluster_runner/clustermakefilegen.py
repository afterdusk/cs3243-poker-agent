#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates the content of a Makefile that'll spawn clients on some servers
# Run with python3 clustermakefilegen.py > ClusterMakefile
# Run resulting makefile with make -f ClusterMakefile -j<number of clusters>

normal_j = 5

servers = {
    # "xcna": 16, # Disable because tcarlson is running a lot of jobs
    "xgpa": 5,
    "xcnb": 20,
    "xcnc": 50,
    "xcnd": 60,
    "xgpb": 3,
    "xgpc": 10,
    "xgpd": 10,
}

blacklist = [
    "xcnb0",
    # Everything below is hogged by tcarlson
    "xcnd45",
    "xcnd46",
    "xcnd47",
    "xcnd48",
    "xcnd49",
    "xcnd50",
    "xcnd51",
    "xcnd52",
    "xcnd53",
    "xcnd54",
    "xcnd55",
    "xcnd56",
    "xcnd57",
    "xcnd58",
    "xcnd59",
]

special_js = {
    "xgpa0": 20,
    "xgpa1": 20,
    "xgpa2": 20,
    "xgpa3": 20,
    "xgpa4": 20,
    "xgpc6": 16,
    "xgpd3": 16,
    # "xcna1": 20, # We'll manually handle the server machine
    "xcnb1": 20,
    "xcnb2": 20,
    "xcnb3": 20,
    "xcnb4": 20,
    "xcnb5": 20,
    "xcnb6": 20,
    "xcnb7": 20,
    "xcnb8": 20,
    "xcnb9": 20,
    "xcnb10": 20,
    "xcnb11": 20,
    "xcnb12": 20,
    "xcnb13": 20,
    "xcnb14": 20,
    "xcnb15": 20,
    "xcnb16": 20,
    "xcnb17": 20,
    "xcnb18": 20,
    "xcnb19": 20,
    "xcnd33": 20,
    "xcnd34": 20,
    "xcnd35": 20,
    "xcnd36": 20,
    "xcnd37": 20,
    "xcnd40": 20,
    "xcnd41": 20,
    "xcnd42": 20,
    "xcnd43": 20,
    "xcnd44": 20,
}

print("SERVERS=\\")
for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        node_name = f"{node_collection_name}{idx}"
        if node_name in blacklist:
            continue
        print(f"{node_name}.comp.nus.edu.sg\\")
print("")

print("KILLSERVERS=\\")
for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        node_name = f"{node_collection_name}{idx}"
        print(f"kill.{node_name}.comp.nus.edu.sg\\")
print("")

print("all: $(SERVERS)\n")
print("killall: $(KILLSERVERS)\n")

for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        node_name = f"{node_collection_name}{idx}"
        print("")

        print(f"kill.{node_name}.comp.nus.edu.sg:")
        print(f"\t-ssh -oBatchMode=yes -oStrictHostKeyChecking=no {node_name}.comp.nus.edu.sg -t \"killall python\"")

        if node_name in blacklist:
            continue

        num_jobs = normal_j
        if node_name in special_js:
            num_jobs = special_js[node_name]
        print(f"{node_name}.comp.nus.edu.sg:")
        print(f"\t-ssh -oBatchMode=yes -oStrictHostKeyChecking=no {node_name}.comp.nus.edu.sg -t \"cd cs3243-poker-agent; bash -cl 'make -j{num_jobs} > /dev/null'\"")
