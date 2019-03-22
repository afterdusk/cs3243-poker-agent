import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class CMAPlayerSpace:
    def __init__(self, taskmaster, name, player_class, num_instances, weight_ranges, initial_sd, num_games, num_rounds, timeout):
        self.name = name
        self.taskmaster = taskmaster
        self.player_class = player_class
        self.num_instances = num_instances
        self.activations = [
                activation_functions.tanh(
                    0, 
                    (float(r[1]) - float(r[0])) / 2, 
                    2, 
                    (float(r[0]) + float(r[1])) / 2) 
                for r in weight_ranges]
        self.initial_sd = initial_sd
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_dir = './cma_logs/' + self.name + '/'
        self.output_state_path = self.output_dir + 'state.txt'
        self.output_log_path = self.output_dir + 'log.txt'

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if os.path.isfile(self.output_state_path):
            print('Loading state from file...')
            with open(self.output_state_path) as state_file:
                self.instances = pickle.load(state_file)
        else:
            print('Generating new state...')
            self.instances = []        
            cma_options = cma.CMAOptions()
            cma_options.set('verbose', -9)
            cma_options.set('verb_disp', -1)
            cma_options.set('verb_log', 0)
            for mean in [[random.uniform(-1, 1) for _ in xrange(len(self.activations))] for _ in xrange(num_instances)]:
                self.instances += [cma.CMAEvolutionStrategy(mean, initial_sd, cma_options)]

        self.begin()

    def begin(self):
        print('Logging...')
        with open(self.output_log_path, 'a') as log_file:
            for (i, instance) in enumerate(self.instances):
                log_file.write('(' + str(i).zfill(2) + ') Weights = ' + ' '.join(str(self.activations[j](x)) for (j, x) in enumerate(instance.result[5])) + '\n')
                log_file.write('(' + str(i).zfill(2) + ') Mean = ' + ' '.join(str(x) for x in instance.result[5]) + '\n')
                log_file.write('(' + str(i).zfill(2) + ') SD =   ' + ' '.join(str(x) for x in instance.result[6]) + '\n')
                log_file.write('(' + str(i).zfill(2) + ') Norm(SD) = ' + str(numpy.linalg.norm(instance.result[6], ord=2)) + '\n')
            log_file.write('\n')
        with open(self.output_state_path, 'wb') as state_file:
            pickle.dump(self.instances, state_file)

        print('Generating jobs...')

        jobs = []    
        particles = [instance.ask() for instance in self.instances]

        for (i, instance) in enumerate(self.instances):
            for (j, particle) in enumerate(particles[i]):
                for (k, other_instance) in enumerate(self.instances):
                    if i == k:
                        continue
                    other_mean = other_instance.result[5]
                    jobs += [[
                        (
                            (self.player_class, [self.activations[l](x) for (l, x) in enumerate(particle)]), 
                            (self.player_class, [self.activations[l](x) for (l, x) in enumerate(other_mean)])
                        ), 
                        (self.num_games, self.num_rounds), 
                        (i, j, k)]]

        print('Running jobs...')
        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, self.timeout, lambda job, outcome: self.callback(job, outcome, jobs, particles, completed_jobs))
    
    def callback(self, job, outcome, jobs, particles, completed_jobs):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(len(jobs)) + ')')
        if len(completed_jobs) < len(jobs):
            return

        print('Updating instances...')
        particle_outcomes = [[0] * len(p) for p in particles]
        for completed_job in completed_jobs:
            particle_outcomes[completed_job[0][2][0]][completed_job[0][2][1]] += completed_job[1]
        for (i, po) in enumerate(particle_outcomes):
            self.instances[i].tell(particles[i], [-float(v) / (self.num_instances - 1) for v in po])

        self.begin()
