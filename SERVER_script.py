from syncengine.client import Client
import config

class TrainerServer:
    def __init__(self):
        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobReq, self.on_request)
        self.client.connect()

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobReq)

    def on_request(self, client, topic, content):
        print("GOT REQUEST", client, topic, content)
        client.send_message([(23, 234, ("on", "ont")), (23, 234, ("on", "ont"))], config.mqttTopicJobRes, True, client.guess_interlocutor_id(topic))

if __name__ == "__main__":
    trainer = TrainerServer()
    trainer.client.mqttc.loop_forever()
