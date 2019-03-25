# Requires Python >=3.6

from sys import argv

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


def all_node_names():
    node_names = []
    for node_collection_name in servers:
        node_names += [f"{node_collection_name}{idx}" for idx in range(servers[node_collection_name])]
    return node_names


def node_name_to_hostname(node_name):
    return f"{node_name}.comp.nus.edu.sg"


def all_node_hostnames():
    return [node_name_to_hostname(n) for n in all_node_names()]


if __name__ == "__main__":
    if len(argv) == 2:
        if argv[-1] == 'hostnames':
            for hostname in all_node_hostnames():
                print(hostname)
            exit()
    print(all_node_names())
    print(all_node_hostnames())
