#!/bin/bash

# Make core counter makefile
python3 gen_core_counter_makefile.py > MakefileCoreCounter

# Count cores
make -f MakefileCoreCounter -j300

# Make MakefileCluster from gathered data
python3 clustermakefilegen.py
