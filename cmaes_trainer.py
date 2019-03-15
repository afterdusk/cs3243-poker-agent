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
NUM_THREADS = 3

cma_instances = []

for (i, mean) in enumerate([random.uniform(0, 1) for _ in xrange(DIMENSIONS)] for _ in xrange(NUM_INSTANCES)):
    print('Preparing CMA instance ' + str(i + 1) + " / " + str(NUM_INSTANCES)) 
    cma_instances += [cma.CMAEvolutionStrategy(mean, INITIAL_SD, CMA_OPTIONS)]

# Get copy of mean of each instance.
cma_means = [instance.result[5] for instance in cma_instances]

# Prepare jobs.
jobs = []
for (i, instance) in enumerate(cma_instances):
    particles = instance.ask()
    for (j, particle) in enumerate(particles):
        for (k, other_mean) in enumerate(cma_means):
            if k == i:
                continue
            jobs += [[i, particle, other_mean]]
jobs_count = multiprocessing.Value('i', len(jobs))
finished_count = multiprocessing.Value('i', 0)

def job_task(job):
    win_count = 0
    current_stack = 0
    other_stack = 0

    for _ in range(0, NUM_GAMES):
        current_player = WeightedPlayer()
        current_player.initWeights(job[1])
        other_player = WeightedPlayer()
        other_player.initWeights(job[2])
        result = play_game(current_player, other_player, NUM_ROUNDS)
        if result['players'][0]['stack'] > result['players'][1]['stack']:
            win_count += 1
        current_stack = result['players'][0]['stack']
        other_stack = result['players'][1]['stack']
    result = 1 if current_stack >= other_stack else 0

    finished_count.value += 1
    print(
            "Progress = " + str(finished_count.value) + " / " + str(jobs_count.value) + 
            "\nInstance = " + str(job[0]) + 
            "\nParticle = " + str(job[1]) + 
            "\nOther Mean = " + str(job[2]) + 
            "\nResult -> " + str(result) + "\n")

    return result

pool = multiprocessing.Pool(NUM_THREADS)
result = pool.map(job_task, jobs)
