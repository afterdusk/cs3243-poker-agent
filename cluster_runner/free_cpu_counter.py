#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Estimates the number of free cores on a machine.

from multiprocessing import cpu_count
from os import getloadavg
from math import ceil

if __name__ == "__main__":
    print(ceil(getloadavg()[0]))
    print(cpu_count())
