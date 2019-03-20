import heapq
from collections import deque
from uuid import uuid4
from time import time


def new_job_id():
    return str(uuid4())


def wrapped_job_data(job_data):
    return (new_job_id(), job_data)


def wrapped_outcome(job_id, outcome):
    return (job_id, outcome)


# O(n)
def heapq_remove_item_at_index(heap, index):
    heap[index] = heap[-1]
    heap.pop()
    heapq.heapify(heap)


class Taskmaster:
    def __init__(self):
        self.job_queue = deque()  # Queue of wrapped job data
        self.timeout_heap = []  # Tuple of (deadline, wrapped job data)
        # Dict of (wrapped job data, max dur, callback) keyed by job ID
        self.job_data = {}

    def schedule_job(self, job, max_duration, callback):
        wrapped_job = wrapped_job_data(job)
        self.job_queue.append(wrapped_job)
        job_id = wrapped_job[0]
        self.job_data[job_id] = (wrapped_job, max_duration, callback)

    def schedule_jobs(self, jobs, max_duration, callback):
        for job in jobs:
            self.schedule_job(job, max_duration, callback)

    def schedule_timeout_job(self, wrapped_job, max_duration):
        heapq.heappush(self.timeout_heap, (time() + max_duration, wrapped_job))

    def get_next_job(self):
        # Try to run timedout jobs first
        if self.timeout_heap:
            next_timeout_job = self.timeout_heap[0]
            if time() > next_timeout_job[0]:
                heapq.heappop(self.timeout_heap)
                next_wrapped_job = next_timeout_job[1]
                job_id = next_wrapped_job[0]
                try:
                    wrapped_job, max_duration, callback = self.job_data[job_id]
                    self.schedule_timeout_job(next_wrapped_job, max_duration)
                    return next_wrapped_job
                except Exception as e:
                    pass

        # Try to get next queued job if possible
        try:
            next_wrapped_job = self.job_queue.popleft()
            job_id = next_wrapped_job[0]
            wrapped_job, max_duration, callback = self.job_data[job_id]
            self.schedule_timeout_job(next_wrapped_job, max_duration)
            return next_wrapped_job
        except Exception as e:
            print("Got error getting next job", e)
            return None

    def handle_outcome(self, wrapped_outcome):
        job_id, outcome = wrapped_outcome

        try:
            # Retrieve data and remove from dict
            # If the job has already been completed, the next line will throw
            # an IndexError
            wrapped_job, max_duration, callback = self.job_data[job_id]
            del self.job_data[job_id]

            # Remove all instances of this job from timeout heap
            while True:
                try:
                    timeout_indices = [j[1] for j in self.timeout_heap]
                    timeout_idx = timeout_indices.index(wrapped_job)
                    heapq_remove_item_at_index(self.timeout_heap, timeout_idx)
                except Exception as e:
                    break

            # Call callback
            callback(wrapped_job[1], outcome)
        except Exception as e:
            print("Received duplicate outcome", e)

