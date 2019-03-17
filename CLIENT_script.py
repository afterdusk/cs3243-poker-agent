from time import sleep
from syncengine.client import Client
from syncengine.taskmaster import wrapped_outcome
import CLIENT_test_arena as bot_arena
import config

class TrainerClient:
    def __init__(self):
        self.client = Client()
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
            trainer.client.mqttc.disconnect()
            return

        # Play game inform server, and request for job
        print("GOT JOB", topic, content)
        job_id, job_data = content
        outcome = bot_arena.train_bots(job_data)
        client.send_message(wrapped_outcome(job_id, outcome), config.mqttTopicJobOutcome, True)
        self.get_new_job()

if __name__ == "__main__":
    trainer = TrainerClient()
    while True:
        trainer.client.connect()
        trainer.client.mqttc.loop_forever()
        print("SLEEPING")
        sleep(10)  # Time to wait before reconnecting
        print("\n\nRECONNECTING")
