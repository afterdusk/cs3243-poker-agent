#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Estimates the number of free cores on a machine.

from multiprocessing import cpu_count
from os import getloadavg
from math import ceil

if __name__ == "__main__":
    raw_free_count = cpu_count() - ceil(getloadavg()[0])
    print(max(0, raw_free_count))
    print(cpu_count())
