# python2 cma2_summarize_log.py cma2_output/epsilon_player_train_1/log.txt | gnuplot -p -e "plot '-' using 1:2 with lines"

import sys
import re
import numpy as np

with open(sys.argv[1], 'r') as log_file:
    log = log_file.read()

match_string = 'Weights = [ .0-9\\-]*\nMean = [ .0-9\\-]*\nSigma = [ .0-9\\-]*'
log_matches = re.findall(match_string, log)

entries = []
for log_match in log_matches:
    lines = log_match.split('\n')
    weights = [float(s) for s in lines[0].split(' ')[2:]]
    mean = [float(s) for s in lines[1].split(' ')[2:]]
    sigma = float(lines[2].split(' ')[2])
    entries += [[weights, mean, sigma, 0]]

distinct_entries = []
for (i, entry) in enumerate(entries):
    if i > 0 and entry[0] == entries[i - 1][0] and entry[1] == entries[i - 1][1] and entry[2] == entries[i - 1][2]:
        continue
    distinct_entries += [entry]
    if len(distinct_entries) > 1:
        distinct_entries[-1][3] = np.linalg.norm(np.array(distinct_entries[-1][1]) - np.array(distinct_entries[-2][1]))

for (i, entry) in enumerate(distinct_entries):
    print(str(i) + ' ' + str(entry[2]) + ' ' + str(entry[3]) + ' ' + ' '.join(str(x) for x in entry[0]))
