import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions
import mtree

class RRTPlayerSpace:
    def __init__(self, taskmaster, name, player_class, seed, weight_ranges, num_games, num_rounds, timeout):
        self.taskmaster = taskmaster
        self.name = name
        self.player_class = player_class
        self.dimensions = len(weight_ranges)
        self.weight_ranges = weight_ranges
        self.num_games = num_games
        self.num_rounds = num_rounds
        self.timeout = timeout
        self.output_dir = './rrt_output/' + self.name + '/'
        self.output_state_path = self.output_dir + 'state.txt'
        self.output_log_path = self.output_dir + 'log.txt'
        self.index = mtree.MTree(self.norm, max_node_size=4)
        self.max_step = 0.1
        self.streak = 0
    
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if os.path.isfile(self.output_state_path):
            print('Loading state from file...')
            with open(self.output_state_path) as state_file:
                (self.points, self.best_point) = pickle.load(state_file)
                self.index.add_all(self.points)
        else:
            print('Generating new state...')
            self.best_point = seed
            self.points = [self.best_point]
            self.index.add(self.best_point)
            self.save_state()

        self.begin()

    def save_state(self): 
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        with open(self.output_state_path, 'wb') as state_file:
            pickle.dump([self.points, self.best_point], state_file)

    def log_result(self):
        with open(self.output_log_path, 'a') as log_file:
            log_file.write('Tree Size = ' + str(len(self.index)) + '\n')
            log_file.write('Weights = ' + ' '.join(str(x) for x in self.get_weights(self.best_point)) + '\n')
            log_file.write('Streak = ' + str(self.streak) + '\n')
            log_file.write('\n')

    def norm(self, x, y):
        return numpy.linalg.norm(numpy.array(x) - numpy.array(y))

    def activation(self, i, x):
        return float(self.weight_ranges[i][0]) + (float(self.weight_ranges[i][1] - self.weight_ranges[i][0])) * (float(x) - (-1)) / 2

    def get_weights(self, particle):
        return [self.activation(i, x) for (i, x) in enumerate(particle)]

    def begin(self):
        self.log_result()

        # RRT Extend
        target_point = [random.uniform(-1, 1) for _ in xrange(self.dimensions)]
        nearest_point = self.index.search(target_point)[0]
        if self.norm(nearest_point, target_point) <= self.max_step:
            new_point = target_point
        else:
            new_point = (numpy.array(nearest_point) + self.max_step * (numpy.array(target_point) - numpy.array(nearest_point))).tolist()
        self.points += [new_point]
        self.index.add(new_point)

        job = [
            (
                (self.player_class, self.get_weights(self.best_point)),
                (self.player_class, self.get_weights(new_point))
            ), 
            (self.num_games, self.num_rounds), 
            ()
        ]
        self.taskmaster.schedule_jobs([job], self.timeout, self.callback)

    def callback(self, job, outcome):
        if outcome == 1:
            self.streak += 1
        else:
            self.best_point = job[0][1][1]
            self.streak = 1

        self.begin()
