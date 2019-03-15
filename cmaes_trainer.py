# Requires pycma (https://github.com/CMA-ES/pycma)

import cma
import itertools
import math
import random
import multiprocessing
from weighted_player import WeightedPlayer
from test_arena import play_game

DIMENSIONS = 7
RANGE = [0.0, 1.0]
INITIAL_SD = 0.3 / 3 # 3SD = 99.7%
CMA_OPTIONS = cma.CMAOptions()
CMA_OPTIONS.set('verbose', -9)
CMA_OPTIONS.set('verb_disp', -1)
CMA_OPTIONS.set('verb_log', 0)
NUM_INSTANCES = 20
NUM_GAMES = 4
NUM_ROUNDS = 101
NUM_THREADS = 23

cma_instances = []

for (i, mean) in enumerate([random.uniform(0, 1) for _ in xrange(DIMENSIONS)] for _ in xrange(NUM_INSTANCES)):
    print('Preparing CMA instance ' + str(i + 1) + " / " + str(NUM_INSTANCES)) 
    cma_instances += [cma.CMAEvolutionStrategy(mean, INITIAL_SD, CMA_OPTIONS)]

while True:
    for instance in cma_instances:
        print(str(instance.result[0]) + " -> " + str(instance.result[1]))

    # Prepare jobs.
    jobs = [] 
    particles = [instance.ask() for instance in cma_instances]

    for i in xrange(NUM_INSTANCES):
        for j in xrange(len(particles[i])):
            for k in xrange(NUM_INSTANCES):
                if k == i:
                    continue
                jobs += [[i, j, k, particles[i][j], cma_instances[k].result[5]]]

    finished_count = multiprocessing.Value('i', 0)
    jobs_count = multiprocessing.Value('i', len(jobs))

    def worker(job):
        win_count = 0
        current_stack = 0
        other_stack = 0

        for _ in range(0, NUM_GAMES):
            current_player = WeightedPlayer()
            current_player.initWeights(job[3])
            other_player = WeightedPlayer()
            other_player.initWeights(job[4])
            result = play_game(current_player, other_player, NUM_ROUNDS)
            if result['players'][0]['stack'] > result['players'][1]['stack']:
                win_count += 1
            current_stack = result['players'][0]['stack']
            other_stack = result['players'][1]['stack']
        result = 1 if current_stack >= other_stack else 0

        finished_count.value += 1
        print("Progress = " + str(finished_count.value) + " / " + str(jobs_count.value)) 

        return result

    pool = multiprocessing.Pool(NUM_THREADS)
    pool_results = pool.map(worker, jobs, 1)

    particle_values = [[0] * len(p) for p in particles]
    for (i, job) in enumerate(jobs):
        particle_values[job[0]][job[1]] += pool_results[i]

    for (i, p) in enumerate(particle_values):
        cma_instances[i].tell(particles[i], [-float(v) / (NUM_INSTANCES - 1) for v in p])
