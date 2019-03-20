# Makefile that launches a bunch of clients in parallel.
# Handles up to 41 jobs.
#
# Usage: make -j<number of jobs>
# E.g.: make -j23

TARGETS=\
    client0\
    client1\
    client2\
    client3\
    client4\
    client5\
    client6\
    client7\
    client8\
    client9\
    client10\
    client11\
    client12\
    client13\
    client14\
    client15\
    client16\
    client17\
    client18\
    client19\
    client20\
    client21\
    client22\
    client23\
    client24\
    client25\
    client26\
    client27\
    client28\
    client29\
    client30\
    client31\
    client32\
    client33\
    client34\
    client35\
    client36\
    client37\
    client38\
    client39\
    client40\

all: bridge_broker $(TARGETS)

bridge_broker:
	~/.linuxbrew/sbin/mosquitto -c mosquitto_client_cluster_broker.conf

$(TARGETS):
	sleep 5
	python CLIENT_script.py
