import cma
import random
import itertools
import math
from player_space import PlayerSpace

class CMAPlayerSpace:
    def __init__(self, task_master, num_dimensions, num_instances):
        PlayerSpace.__init__(self, task_master)
        self.num_dimensions = num_dimensions
        self.num_instances = num_instances

        self.instances = []        
        cma_options = cma.CMAOptions()
        cma_options.set('verbose', -9)
        cma_options.set('verb_disp', -1)
        cma_options.set('verb_log', 0)
        for mean in enumerate([random.uniform(-1, 1) for _ in xrange(num_dimensions)] for _ in xrange(num_instances)):
            self.instances += [cma.CMAEvolutionStrategy(mean, 0.2 / 3, cma_options)]

    def begin(self):
        jobs = []    
        particles = [instance.ask() for instance in self.instances()]

        for (i, instance) in enumerate(self.instances):
            for (j, particle) in enumerate(instance.ask()):
                for (k, other_instance) in enumerate(self.instances):
                    if i == k:
                        continue
                    other_mean = other_instance.result[5]
                    jobs += [[('WeightedPlayer', particle), ('WeightedPlayer', other_mean), (4, 101), (i, j, k)]]

        completed_jobs = []
        task_master.scheduleJobs(jobs, 5, lambda job, outcome: self.callback(job, outcome, len(jobs), completed_jobs))
    
    def callback(self, job, outcome, num_jobs, completed_jobs):
        completed_jobs += [(job, outcome)]
        if len(completed_jobs) < len(jobs):
            return

        particle_outcomes = [[0] * len(p) for p in particles]
        for completed_job in completed_jobs:
            particle_outcomes[completed_job[3][0]][completed_job[3][1]] += completed_job[1]
        for (i, po) in enumerate(particle_outcomes):
            instances[i].tell(particles[i], [-float(v) / (self.num_instances - 1) for v in po])

        self.begin()
