from syncengine.client import Client
import config
import SERVER_bot_trainer as bot_trainer

class TrainerServer:
    def __init__(self):
        bot_trainer.init()

        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobReq, self.on_request)
        self.client.register_callback(config.mqttTopicJobOutcome, self.on_outcome)
        self.client.connect()

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobReq)

    def on_request(self, client, topic, content):
        print("GOT GAME REQUEST", topic, content)
        nextMatch = bot_trainer.getNextMatch()
        if nextMatch:
            client.send_message(nextMatch, config.mqttTopicJobRes, True, client.guess_interlocutor_id(topic))

    def on_outcome(self, client, topic, content):
        # TODO: THIS ISN'T CALLED FOR OSME REASON
        print("GOT OUTCOME", topic, content)
        bot_trainer.receiveOutcome(outcome)

if __name__ == "__main__":
    trainer = TrainerServer()
    trainer.client.mqttc.loop_forever()
