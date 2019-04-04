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


blacklist_node_names = [
    "xcna1",  # Manually manage the server's server
    "xcnd32",  # Si Jie's group is training here
    "xcnd9",  # Somehow doesn't respond to SSH
]
blacklist = [node_name_to_hostname(n) for n in blacklist_node_names]


def all_whitelisted_node_hostnames():
    return [h for h in all_node_hostnames() if h not in blacklist]


if __name__ == "__main__":
    if len(argv) == 2:
        if argv[-1] == 'hostnames':
            for hostname in all_node_hostnames():
                print(hostname)
            exit()
        if argv[-1] == 'whitelistedhostnames':
            for hostname in all_whitelisted_node_hostnames():
                print(hostname)
            exit()
    print(all_node_names())
    print(all_node_hostnames())
