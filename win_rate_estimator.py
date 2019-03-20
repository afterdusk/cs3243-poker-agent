from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.engine.card import Card
import multiprocessing
from datetime import datetime

start = datetime.now()

def estimate(hole_cards):                        
    return estimate_hole_card_win_rate(100000, 2, [Card.from_id(i) for i in hole_cards], [])

jobs = []
for h1 in xrange(1, 53):
    for h2 in xrange(1, 53):
        if h1 < h2:
            jobs += [[h1, h2]]

def job((h1, h2)):
    win_rate = estimate([h1, h2])
    print(h1, h2, win_rate)
    return win_rate

p = multiprocessing.Pool(23)
results = p.map(job, jobs)
win_rates = [[0] * 52 for _ in xrange(0, 52)]

for (i, result) in enumerate(results):
    win_rates[jobs[i][0] - 1][jobs[i][1] - 1] = result
    win_rates[jobs[i][1] - 1][jobs[i][0] - 1] = result

end = datetime.now()

print(win_rates)
print('Time taken = ' + str((end - start).total_seconds()) + ' s')

