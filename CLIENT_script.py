from time import sleep
from os import getpid
from socket import gethostname
from syncengine.client import Client
from syncengine.taskmaster import wrapped_outcome
import sys
import CLIENT_stadium as stadium
import config


class TrainerClient:
    def __init__(self, client_id=None):
        self.client = Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobRes, self.on_job)

    def connect(self):
        self.client.connect()

    def get_new_job(self):
        self.client.send_message(None, config.mqttTopicJobReq, True)

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobRes, True)
        # Request for job
        self.get_new_job()

    def on_job(self, client, topic, content):
        print("")

        # Disconnect if no job
        if content is None:
            print("RETRENCHED", topic, content)
            sleep(10)  # Time to wait before reconnecting
            self.get_new_job()
            return

        # Play game inform server, and request for job
        print("GOT JOB", topic, content)
        job_id, job_data = content
        outcome = stadium.train_bots(job_data)
        message = wrapped_outcome(job_id, outcome)
        client.send_message(message, config.mqttTopicJobOutcome, True)
        self.get_new_job()


if __name__ == "__main__":
    client_id = gethostname() + '.' + str(getpid())
    trainer = TrainerClient(client_id)
    trainer.client.connect()
    trainer.client.mqttc.loop_forever()
