from pypokerengine.utils.fast_card_utils import estimate_hole_card_win_rate
from pypokerengine.engine.card import Card
import multiprocessing
from datetime import datetime
import numpy as np

def estimate(hole_cards): 
    return estimate_hole_card_win_rate(100000, np.ubyte(hole_cards), np.ubyte([]))

def job((h1, h2)):
    win_rate = estimate([h1, h2])
    print(h1, h2, win_rate)
    return win_rate

def run_estimation():
    start = datetime.now()
    jobs = []
    for h1 in xrange(1, 53):
        for h2 in xrange(1, 53):
            if h1 < h2:
                jobs += [[h1, h2]]

    p = multiprocessing.Pool(1)
    results = p.map(job, jobs)
    win_rates = [[0] * 52 for _ in xrange(0, 52)]
    for (i, result) in enumerate(results):
        win_rates[jobs[i][0] - 1][jobs[i][1] - 1] = result
        win_rates[jobs[i][1] - 1][jobs[i][0] - 1] = result

    end = datetime.now()
    with open('win_rate_estimates.txt', 'w') as f:
        f.write(str(win_rates))
    print('Time taken = ' + str((end - start).total_seconds()) + ' s')

job((1, 2))
