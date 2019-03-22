import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class CMASinglePlayerSpace:
    def __init__(self, taskmaster, name, player_class, num_particles, num_eval_particles, weight_ranges, num_games, num_rounds, timeout):
        self.name = name
        self.taskmaster = taskmaster
        self.player_class = player_class
        self.activations = [
                activation_functions.tanh(
                    0, 
                    (float(r[1]) - float(r[0])) / 2, 
                    2, 
                    (float(r[0]) + float(r[1])) / 2) 
                for r in weight_ranges]
        self.num_particles = num_particles
        self.num_eval_particles = num_eval_particles
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_dir = './cma_output/' + self.name + '/'
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
            cma_options.set('popsize', self.num_particles)
            self.instance = cma.CMAEvolutionStrategy(
                    [[0] * len(self.activations)], # Origin centered
                    1.0 / 2, # 2SD = 1.0 -> 95% within [-1, 1]
                    cma_options)

        self.begin()

    def begin(self):
        print('Logging...')
        with open(self.output_log_path, 'a') as log_file:
            log_file.write('Mean = ' + ' '.join(str(x) for x in self.instance.result[5]) + '\n')
            log_file.write('SD =   ' + ' '.join(str(x) for x in self.instance.result[6]) + '\n')
            log_file.write('Norm(SD) = ' + str(numpy.linalg.norm(self.instance.result[6], ord=2)) + '\n')
            log_file.write('\n')
        with open(self.output_state_path, 'wb') as state_file:
            pickle.dump(self.instance, state_file)

        print('Generating jobs...')

        jobs = []    
        particles = self.instance.ask()

        for (i, particle) in enumerate(particles):
            other_particles = [[random.uniform(-1, 1) for _ in xrange(len(self.activations))] for _ in xrange(self.num_eval_particles)]
            for (j, other_particle) in enumerate(other_particles):
                jobs += [[
                    (
                        (self.player_class, [self.activations[l](x) for (l, x) in enumerate(particle)]), 
                        (self.player_class, [self.activations[l](x) for (l, x) in enumerate(other_particle)])
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
        particle_win_rates = [0] * len(particles)
        for completed_job in completed_jobs:
            particle_win_rates[completed_job[0][2][0]] += completed_job[1]
        particle_win_rates = [-float(wr) / self.num_eval_particles for wr in particle_win_rates]
        self.instance.tell(particles, particle_win_rates)

        self.begin()
