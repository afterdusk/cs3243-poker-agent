import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class ProfilePlayerSpace:
    def __init__(self, taskmaster, name, player_class, weight_ranges, evaluations_per_particle, samples_per_evaluation, num_games, num_rounds, timeout):
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
        self.evaluations_per_particle = evaluations_per_particle
        self.samples_per_evaluation = samples_per_evaluation
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_dir = './cma_output/' + self.name + '/'
        self.output_state_path = self.output_dir + 'state.txt'
        self.output_log_path = self.output_dir + 'log.txt'

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.begin()

    def sample(self):
        return [random.uniform(-1, 1) for _ in xrange(len(self.activations))]

    def begin(self):
        jobs = [] 

        particle = self.sample()
        other_particles = [self.sample() for _ in xrange(self.evaluations_per_particle * self.samples_per_evaluation)]

        for other_particle in other_particles:
            jobs += [[
                (
                    (self.player_class, [self.activations[l](x) for (l, x) in enumerate(particle)]), 
                    (self.player_class, [self.activations[l](x) for (l, x) in enumerate(other_particle)])
                ), 
                (self.num_games, self.num_rounds), 
                ()]]

        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, self.timeout, lambda job, outcome: self.callback(job, outcome, jobs, completed_jobs, particle))
    
    def callback(self, job, outcome, jobs, completed_jobs, particle):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(len(jobs)) + ')')
        if len(completed_jobs) < len(jobs):
            return

        outcomes = [j[1] for j in completed_jobs]
        evaluations = [float(sum(outcomes[i * self.samples_per_evaluation : (i + 1) * self.samples_per_evaluation])) / self.samples_per_evaluation for i in xrange(self.evaluations_per_particle)]

        with open(self.output_log_path, 'a') as log_file:
            log_file.write('Particle = ' + ' '.join(str(x) for x in particle))
            for (i, evaluation) in enumerate(evaluations):
                log_file.write('(' + str(i).zfill(2) + ') Eval = ' + str(evaluation) + '\n')
            log_file.write('\n')

        self.begin()
