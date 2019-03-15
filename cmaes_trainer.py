# Requires pycma (https://github.com/CMA-ES/pycma)

import cma
import itertools
import math
from weighted_player import WeightedPlayer
from test_arena import play_game

DIMENSIONS = 7
RANGE =[-1.0, 1.0]
INITIAL_INTERVAL_COUNT = 2 # >= 2
INITIAL_INTERVALS = [RANGE[0] + i * (RANGE[1] - RANGE[0]) / (INITIAL_INTERVAL_COUNT - 1) for i in xrange(0, INITIAL_INTERVAL_COUNT)]
INITIAL_SD = math.sqrt(2) * (RANGE[1] - RANGE[0]) / (INITIAL_INTERVAL_COUNT - 1) / 2 / 3 # 3SD = 99.7%
CMA_OPTIONS = cma.CMAOptions()
CMA_OPTIONS.set('verbose', -9)
CMA_OPTIONS.set('verb_disp', -1)
CMA_OPTIONS.set('verb_log', 0)
NUM_GAMES = 4
NUM_ROUNDS = 101

cma_instances = [
        cma.CMAEvolutionStrategy(mean, INITIAL_SD, CMA_OPTIONS)
        for mean in list(itertools.product(*([INITIAL_INTERVALS] * DIMENSIONS)))]

cma_means = [instance.result[5] for instance in cma_instances]

for (i, instance) in enumerate(cma_instances):
    particles = instance.ask()
    particle_win_rates = [0] * len(particles)

    for (j, particle) in enumerate(particles):
        particle_win_count = 0

        # Play against each other mean, and get number of wins.
        for (k, other_mean) in enumerate(cma_means):
            if k == i:
                continue

            # For other mean, play NUM_GAMES games with NUM_ROUNDS rounds each,
            # and determine who wins via stack size.
            win_count = 0
            current_stack = 0
            other_stack = 0
            for _ in range(0, NUM_GAMES):
                current_player = WeightedPlayer()
                current_player.initWeights(particle)
                other_player = WeightedPlayer()
                other_player.initWeights(other_mean)
                result = play_game(current_player, other_player, NUM_ROUNDS)
                if result['players'][0]['stack'] > result['players'][1]['stack']:
                    win_count += 1
                current_stack = result['players'][0]['stack']
                other_stack = result['players'][1]['stack']
            
            if current_stack > other_stack:
                particle_win_count += 1

            print("Instance = " + str(i) + ", Particle = " + str(j) + ", Opponent = " + str(k) + " -> " + str(particle_win_count))
        
        # Normalize win count over number of other instances.
        particle_win_rates[j] = particle_win_count / (len(cma_instances) - 1)
    
    # Update instance.
    instance.tell(particles, particle_win_rates)

