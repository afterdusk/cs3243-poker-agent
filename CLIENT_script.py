from syncengine.client import Client
import config

class TrainerClient:
    def __init__(self):
        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobRes, self.on_job)
        self.client.connect()

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobRes, True)
        # Request for job
        client.send_message([(23, 234, ("on", "ont")), (23, 234, ("on", "ont"))], config.mqttTopicJobReq, True)

    def on_job(self, client, topic, content):
        print("GOT JOB", client, topic, content)

if __name__ == "__main__":
    trainer = TrainerClient()
    trainer.client.mqttc.loop_forever()
