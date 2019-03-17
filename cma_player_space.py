import cma
import random
import itertools
import math

class CMAPlayerSpace:
    def __init__(self, taskmaster, num_dimensions, num_instances, initial_sd, num_games, num_rounds):
        self.taskmaster = taskmaster
        self.num_dimensions = num_dimensions
        self.num_instances = num_instances
        self.initial_sd = initial_sd
        self.num_games = num_games
        self.num_rounds = num_rounds

        self.instances = []        
        cma_options = cma.CMAOptions()
        cma_options.set('verbose', -9)
        cma_options.set('verb_disp', -1)
        cma_options.set('verb_log', 0)
        for mean in [[random.uniform(-1, 1) for _ in xrange(num_dimensions)] for _ in xrange(num_instances)]:
            self.instances += [cma.CMAEvolutionStrategy(mean, initial_sd, cma_options)]

        self.begin()

    def begin(self):
        jobs = []    
        particles = [instance.ask() for instance in self.instances]

        for (i, instance) in enumerate(self.instances):
            for (j, particle) in enumerate(instance.ask()):
                for (k, other_instance) in enumerate(self.instances):
                    if i == k:
                        continue
                    other_mean = other_instance.result[5]
                    jobs += [[
                        (('WeightedPlayer', particle), ('WeightedPlayer', other_mean)), 
                        (self.num_games, self.num_rounds), 
                        (i, j, k)]]

        completed_jobs = []
        self.taskmaster.schedule_jobs(jobs, 5, lambda job, outcome: self.callback(job, outcome, len(jobs), completed_jobs))
    
    def callback(self, job, outcome, num_jobs, completed_jobs):
        completed_jobs += [(job, outcome)]
        print('Progress (' + str(len(completed_jobs)) + '/' + str(num_jobs) + ')')
        if len(completed_jobs) < num_jobs:
            return

        particle_outcomes = [[0] * len(p) for p in particles]
        for completed_job in completed_jobs:
            particle_outcomes[completed_job[3][0]][completed_job[3][1]] += completed_job[1]
        for (i, po) in enumerate(particle_outcomes):
            instances[i].tell(particles[i], [-float(v) / (self.num_instances - 1) for v in po])

        self.begin()
