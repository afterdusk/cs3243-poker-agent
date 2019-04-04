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
for (i, entry) in enumerate(entries):
    if i == 0:
        continue
    entry[3] = np.linalg.norm(np.array(entry[0]) - np.array(entries[i - 1][0]))

for (i, entry) in enumerate(entries):
    print(str(i) + ' ' + str(entry[2]) + ' ' + str(entry[3]) + ' ' + ' '.join(str(x) for x in entry[0]))
