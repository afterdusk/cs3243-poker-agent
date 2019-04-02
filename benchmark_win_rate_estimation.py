import numpy
import time

from pypokerengine.utils.card_utils import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from fast_monte_carlo import estimate_win_rate

NUM_SAMPLES = 10000
NUM_SIMULATIONS = 200

def sample(num_community):
    selection = numpy.random.choice(range(1, 53), 2 + num_community).tolist()
    return (selection[0:2], selection[2:])

def time_pypokerengine(hole, community, num_sim):
    hole = [Card.from_id(c) for c in hole]
    community = [Card.from_id(c) for c in community]

    start = time.clock()
    estimate_hole_card_win_rate(num_sim, 2, hole, community)
    return time.clock() - start

def time_fast_monte_carlo(hole, community, num_sim):
    (hole, community) = sample(num_community)

    start = time.clock()
    estimate_win_rate(num_sim, hole, community)
    return time.clock() - start

for num_community in [0, 3, 4, 5]:
  print('Benchmarking for ' + str(num_community) + ' community cards...')

  pypokerengine_timings = []
  fast_monte_carlo_timings = []
  for i in xrange(NUM_SAMPLES):
    (hole, community) = sample(num_community)
    pypokerengine_timings += [time_pypokerengine(hole, community, NUM_SIMULATIONS)]
    fast_monte_carlo_timings += [time_fast_monte_carlo(hole, community, NUM_SIMULATIONS)]

  print('pypokerengine: Mean = ' + str(numpy.mean(pypokerengine_timings)) + ', Std = ' + str(numpy.std(pypokerengine_timings, ddof=1)))
  print('fast_monte_carlo: Mean = ' + str(numpy.mean(fast_monte_carlo_timings)) + ', Std = ' + str(numpy.std(fast_monte_carlo_timings, ddof=1)))
  print('')
