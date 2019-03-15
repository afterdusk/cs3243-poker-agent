from syncengine.client import Client
import CLIENT_test_arena as bot_arena
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
        client.send_message(None, config.mqttTopicJobReq, True)

    def on_job(self, client, topic, content):
        print("GOT JOB", topic, content)
        # Play game
        outcome = bot_arena.train_bots(content)
        print("OSNTO")
        print("oircoec", outcome, config.mqttTopicJobOutcome)
        client.send_message(outcome, config.mqttTopicJobOutcome, True)

if __name__ == "__main__":
    trainer = TrainerClient()
    trainer.client.mqttc.loop_forever()
