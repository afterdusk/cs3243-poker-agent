import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class ProfilePlayerSpace:
    def __init__(self, taskmaster, player_class, weights_file_path, weight_ranges, evaluations_per_weight, num_games, num_rounds, timeout):
        self.taskmaster = taskmaster
        self.player_class = player_class
        self.dimensions = len(weight_ranges)
        self.weight_ranges = weight_ranges
        self.evaluations_per_weight = evaluations_per_weight
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_path = weights_file_path + '.output'
        self.count = 0
        self.weights = []

        with open(weights_file_path, 'r') as weights_file:
            for line in weights_file:
                line = line.rstrip('\n').rstrip('\r')
                splitted = line.split(' ')
                self.weights += [(
                        splitted[0],
                        [float(v) for v in splitted[1:]])]

        self.begin()

    def activation(self, i, x):
        return float(self.weight_ranges[i][0]) + (float(self.weight_ranges[i][1] - self.weight_ranges[i][0])) * (float(x) - (-1)) / 2

    def sample(self):
        return [random.uniform(-1, 1) for _ in xrange(self.dimensions)]
    
    def get_weights(self, particle):
        return [self.activation(i, x) for (i, x) in enumerate(particle)]

    def begin(self):
        if self.count >= len(self.weights):
            return

        jobs = [] 
        
        print('Generating jobs...')

        # Evaluation test
        evaluation_other_particles = [self.sample() for _ in xrange(self.evaluations_per_weight)]
        for other_particle in evaluation_other_particles:
            jobs += [[
                (
                    (self.player_class, self.weights[self.count][1]), 
                    (self.player_class, self.get_weights(other_particle))
                ), 
                (self.num_games, self.num_rounds), 
                ()]]

        print('Running jobs...')
        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, self.timeout, lambda job, outcome: self.callback(job, outcome, jobs, completed_jobs))
    
    def callback(self, job, outcome, jobs, completed_jobs):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(len(jobs)) + ')')
        if len(completed_jobs) < len(jobs):
            return

        wins = sum(1 for j in completed_jobs if j[1][0] >= j[1][1])
        winrate = float(wins) / len(completed_jobs)

        with open(self.output_path, 'a') as output_file:
            output_file.write(self.weights[self.count][0] + ' ' + str(winrate) + '\n')
        
        self.count += 1
        self.begin()
