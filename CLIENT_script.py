from syncengine.client import Client
import CLIENT_test_arena as bot_arena
import config

class TrainerClient:
    def __init__(self):
        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobRes, self.on_job)
        self.client.connect()

    def get_new_job(self):
        self.client.send_message(None, config.mqttTopicJobReq, True)

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobRes, True)
        # Request for job
        self.get_new_job()

    def on_job(self, client, topic, content):
        print("GOT JOB", topic, content)
        # Play game inform server, and request for job
        outcome = bot_arena.train_bots(content)
        client.send_message(outcome, config.mqttTopicJobOutcome, True)
        self.get_new_job()

if __name__ == "__main__":
    trainer = TrainerClient()
    trainer.client.mqttc.loop_forever()
