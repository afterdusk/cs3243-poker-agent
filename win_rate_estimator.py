import fast_monte_carlo
import multiprocessing
from datetime import datetime

def estimate(hole_cards): 
    return fast_monte_carlo.estimate_win_rate(100000, hole_cards, [])

def job(hs):
    h1, h2 = hs
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

run_estimation()
