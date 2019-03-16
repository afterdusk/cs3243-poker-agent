# Requires pycma (https://github.com/CMA-ES/pycma)

import cma
import itertools
import math
import random
import multiprocessing
import time
import Queue
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

manager = multiprocessing.Manager()

instances = []
for (i, mean) in enumerate([random.uniform(0, 1) for _ in xrange(DIMENSIONS)] for _ in xrange(NUM_INSTANCES)):
    print('Preparing CMA instance ' + str(i + 1) + " / " + str(NUM_INSTANCES)) 
    instances += [cma.CMAEvolutionStrategy(mean, INITIAL_SD, CMA_OPTIONS)]

with open('cmaes_trainer_log.txt', 'w') as _:
    None
generation = 0
while True:
    with open('cmaes_trainer_log.txt', 'a') as log_file:
        log_file.write('Generation = ' + str(generation) + '\n')
        for instance in instances:
            log_file.write(' '.join(str(x) for x in instance.result[5]) + '\n')
            print(' '.join(str(x) for x in instance.result[5]))
    particles = [instance.ask() for instance in instances]

    jobs = manager.list()
    job_index_queue = manager.Queue()
    results = manager.list()
    for (i, j, k) in itertools.product(xrange(NUM_INSTANCES), xrange(len(particles[i])), xrange(NUM_INSTANCES)):
        if k == i:
            continue
        job_index_queue.put_nowait(len(jobs))
        job = [i, j, k, particles[i][j], instances[k].result[5]]
        jobs += [job]
        results += [0]

    def worker(jobs, job_index_queue, results):
        while True:
            try:
                job_index = job_index_queue.get_nowait()
            except Queue.Empty:
                break
            job = jobs[job_index]
            print("Processing = " + str(len(jobs) - job_index_queue.qsize()) + " / " + str(len(jobs)))

            win_count = 0
            current_stack = 0
            other_stack = 0

            for _ in xrange(NUM_GAMES):
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
            results[job_index] += result

    processes = []
    for i in range(NUM_THREADS):
        process = multiprocessing.Process(target=worker, args=(jobs, job_index_queue, results))
        process.start()
        processes += [process]

    for process in processes:
        process.join()

    particle_values = [[0] * len(p) for p in particles]
    for (i, job) in enumerate(jobs):
        particle_values[job[0]][job[1]] += results[i]

    for (i, p) in enumerate(particle_values):
        instances[i].tell(particles[i], [-float(v) / (NUM_INSTANCES - 1) for v in p])

    generation += 1 
