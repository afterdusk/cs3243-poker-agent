#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Counts the number of free cores on a machine.
# Requires psutil library.

import psutil


def count_free_cpus():
    cpu_usage = psutil.cpu_percent(interval=10, percpu=True)
    return len([x for x in cpu_usage if x < 1])


if __name__ == "__main__":
    print(count_free_cpus())
    print(psutil.cpu_count())
