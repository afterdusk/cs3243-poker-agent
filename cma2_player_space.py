import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class CMA2PlayerSpace:
    def __init__(self, taskmaster, name, player_class, pop_size, weight_ranges, num_games, num_rounds, timeout):
        self.name = name
        self.taskmaster = taskmaster
        self.player_class = player_class
        self.pop_size = pop_size
        self.dimensions = len(weight_ranges)
        self.weight_ranges = weight_ranges
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_dir = './cma2_output/' + self.name + '/'
        self.output_state_path = self.output_dir + 'state.txt'
        self.output_log_path = self.output_dir + 'log.txt'

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if os.path.isfile(self.output_state_path):
            print('Loading state from file...')
            with open(self.output_state_path) as state_file:
                self.instance = pickle.load(state_file)
        else:
            print('Generating new state...')
            cma_options = cma.CMAOptions()
            cma_options.set('verbose', -9)
            cma_options.set('verb_disp', -1)
            cma_options.set('verb_log', 0)
            cma_options.set('popsize', pop_size)
            self.instance = cma.CMAEvolutionStrategy(
                    [0] * self.dimensions, # Origin centered
                    0.34, # 3SD covering [-1, 1]
                    cma_options)

        self.begin()

    def activation(self, i, x):
        return float(self.weight_ranges[i][0]) + (float(self.weight_ranges[i][1] - self.weight_ranges[i][0])) * (float(x) - (-1)) / 2

    def get_weights(self, particle):
        return [self.activation(i, x) for (i, x) in enumerate(particle)]

    def get_current_mean(self):
        return self.instance.result[5]
    
    def get_current_sd(self):
        return self.instance.result[6]

    def get_current_sigma(self):
        return self.instance.sigma

    def begin(self):
        print('Logging...')
        with open(self.output_log_path, 'a') as log_file:
            log_file.write('Weights = ' + ' '.join(str(x) for x in self.get_weights(self.get_current_mean())) + '\n')
            log_file.write('Mean = ' + ' '.join(str(x) for x in self.get_current_mean()) + '\n')
            log_file.write('Sigma = ' + str(self.get_current_sigma()) + '\n')
        with open(self.output_state_path, 'wb') as state_file:
            pickle.dump(self.instance, state_file)

        print('Generating jobs...')

        # Rejection sampling of particles.
        particles = []
        for _ in xrange(self.instance.popsize):
            particle = self.instance.ask(1)[0]
            while not all(True if v >= -1 and v <= 1 else False for v in particle):
                particle = self.instance.ask(1)[0]
            particles += [particle]

        jobs = []
        for (i, particle1) in enumerate(particles):
            for (j, particle2) in enumerate(particles):
                if i == j:
                    continue
                jobs += [[
                    (
                        (self.player_class, self.get_weights(particle1)), 
                        (self.player_class, self.get_weights(particle2))
                    ), 
                    (self.num_games, self.num_rounds), 
                    (i, j)]]

        print('Running jobs...')
        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, self.timeout, lambda job, outcome: self.callback(job, outcome, jobs, particles, completed_jobs))
    
    def callback(self, job, outcome, jobs, particles, completed_jobs):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(len(jobs)) + ')')
        if len(completed_jobs) < len(jobs):
            return

        print('Updating instances...')
        particle_wins = [0] * len(particles)
        for completed_job in completed_jobs:
            particle_wins[completed_job[0][2][0]] += completed_job[1]
            particle_wins[completed_job[0][2][1]] += 1 - completed_job[1]
        self.instance.tell(particles, [-w for w in particle_wins], check_points=False)
        
        print('Logging...')
        with open(self.output_log_path, 'a') as log_file:
            for (i, particle) in enumerate(particles):
                log_file.write('(' + str(i).zfill(2) + ') Weights = ' + ' '.join(str(x) for x in self.get_weights(particle)) + '\n')
                log_file.write('(' + str(i).zfill(2) + ') Particle = ' + ' '.join(str(x) for x in particle) + '\n')
                log_file.write('(' + str(i).zfill(2) + ') Evaluation = ' + str(particle_wins[i]) + '\n')
            log_file.write('\n')

        self.begin()
