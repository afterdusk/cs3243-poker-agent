# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates the content of a Makefile that'll spawn clients on some servers
# Run with python3 clustermakefilegen.py > ClusterMakefile
# Run resulting makefile with make -f ClusterMakefile -j<number of clusters>

normal_j = 3

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

blacklist = ["xcnb0"]

special_js = {
    "xgpc0": 30,
    "xgpd6": 16,
    "xgpc6": 25,
    # "xcna1": 20, # We'll manually handle the server machine
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
    "xcnb19": 20
}

print("SERVERS=\\")
for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        node_name = f"{node_collection_name}{idx}"
        if node_name in blacklist:
            continue
        print(f"{node_name}.comp.nus.edu.sg\\")
print("")

print("all: $(SERVERS)\n")

for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        num_jobs = normal_j
        node_name = f"{node_collection_name}{idx}"
        if node_name in blacklist:
            continue
        if node_name in special_js:
            num_jobs = special_js[node_name]
        print(f"{node_name}.comp.nus.edu.sg:")
        print(f"\tssh -o \"StrictHostKeyChecking no\" {node_name}.comp.nus.edu.sg -t \"cd cs3243-poker-agent; bash -cl 'make -j{num_jobs}'\"")
