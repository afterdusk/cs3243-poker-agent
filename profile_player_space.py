import cma
import random
import itertools
import math
import numpy
import pickle
import os
import activation_functions

class ProfilePlayerSpace:
    def __init__(self, taskmaster, name, player_class, weight_ranges, evaluations_per_particle, samples_per_evaluation, transitivity_checks, num_games, num_rounds, timeout):
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
        self.transitivity_checks = transitivity_checks
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
    
    def get_weights(self, particle):
        return [self.activations[i](x) for (i, x) in enumerate(particle)]

    def begin(self):
        jobs = [] 
        
        print('Generating jobs...')

        # Evaluation test
        evaluation_particle = self.sample()
        evaluation_other_particles = [self.sample() for _ in xrange(self.evaluations_per_particle * self.samples_per_evaluation)]
        for other_particle in evaluation_other_particles:
            jobs += [[
                (
                    (self.player_class, self.get_weights(evaluation_particle)), 
                    (self.player_class, self.get_weights(other_particle))
                ), 
                (self.num_games, self.num_rounds), 
                ('Evaluation')]]

        # Transitivity test
        for i in xrange(self.transitivity_checks):
            transitivity_particles = [self.sample() for _ in xrange(3)]
            jobs += [[
                (
                    (self.player_class, self.get_weights(transitivity_particles[0])),
                    (self.player_class, self.get_weights(transitivity_particles[1]))
                ),
                (self.num_games, self.num_rounds),
                ('Transitivity', i, 0)]]
            jobs += [[
                (
                    (self.player_class, self.get_weights(transitivity_particles[1])),
                    (self.player_class, self.get_weights(transitivity_particles[2]))
                ),
                (self.num_games, self.num_rounds),
                ('Transitivity', i, 1)]]
            jobs += [[
                (
                    (self.player_class, self.get_weights(transitivity_particles[2])),
                    (self.player_class, self.get_weights(transitivity_particles[0]))
                ),
                (self.num_games, self.num_rounds),
                ('Transitivity', i, 2)]]
        

        print('Running jobs...')
        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, self.timeout, lambda job, outcome: self.callback(job, outcome, jobs, completed_jobs))
    
    def callback(self, job, outcome, jobs, completed_jobs):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(len(jobs)) + ')')
        if len(completed_jobs) < len(jobs):
            return

        print('Calculating statistics...')
        evaluation_jobs = [j for j in completed_jobs if j[0][2][0] == 'Evaluation']
        evaluation_outcomes = [j[1] for j in evaluation_jobs]
        evaluations = [float(sum(evaluation_outcomes[i * self.samples_per_evaluation : (i + 1) * self.samples_per_evaluation])) / self.samples_per_evaluation for i in xrange(self.evaluations_per_particle)]

        transitivity_jobs = [j for j in completed_jobs if j[0][2][0] == 'Transitivity']
        pass_count = 0
        for i in xrange(transitivity_checks):
            case_jobs = [j for j in transitivity_jobs if j[0][2][1] == i]
            case_jobs = sorted(case_jobs, key=lambda j: j[0][2][2])
            if case_jobs[0][1] == case_jobs[1][1] and case_jobs[1][1] == case_jobs[2][1]:
                pass_count += 0
            else:
                pass_count += 1

        print('Logging...')
        with open(self.output_log_path, 'a') as log_file:
            log_file.write('Evaluation = ' + ' '.join([str(x) for x in evaluations]) + '\n')
            log_file.write('Transitivity = ' + str(float(pass_count) / self.transitivity_checks) + '\n')
            log_file.write('\n')

        self.begin()
