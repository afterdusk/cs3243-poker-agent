# NOTE: THIS IS A PYTHON >=3.6 PROGRAM
# Generates the content of a Makefile that'll spawn clients on some servers

normal_j = 3

servers = {
    "xcna": 16,
    "xgpa": 5,
    "xcnb": 20,
    "xcnc": 50,
    "xcnd": 60,
    "xgpb": 3,
    "xgpc": 10,
    "xgpd": 10,
}

special_js = {
    "xcna1": 24,
    "xgpc0": 30,
    "xgpd6": 16,
    "xgpc6": 25,
    "xcnb3": 24,
    "xcnb2": 24,
    "xcnb7": 24,
    "xcnb8": 24
}

print("SERVERS=\\")
for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        print(f"{node_collection_name}{idx}.comp.nus.edu.sg\\")
print("")

print("all: $(SERVERS)\n")

for node_collection_name in servers:
    for idx in range(servers[node_collection_name]):
        num_jobs = normal_j
        node_name = f"{node_collection_name}{idx}"
        if node_name in special_js:
            num_jobs = special_js[node_name]
        print(f"{node_name}.comp.nus.edu.sg:")
        print(f"\tssh {node_name}.comp.nus.edu.sg -t \"make -j{num_jobs}\"")
