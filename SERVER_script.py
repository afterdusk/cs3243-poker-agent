from syncengine.client import Client
from syncengine.taskmaster import Taskmaster
import config

# Import player spaces here
import SERVER_david_playerspace as david_playerspace
from cma_player_space import CMAPlayerSpace
from cma_single_player_space import CMASinglePlayerSpace

def createPlayerSpaces(taskmaster):
    # Init player spaces here
    # david_playerspace.init(taskmaster)
    return [
        CMASinglePlayerSpace(
            taskmaster, # taskmaster
            'wise_player_test_single_1', # name
            'WisePlayer', # class
            100, # num particles
            1000, # num eval particles
            [ # weight ranges
                [0, 1], 
                [-1, 0],
                [-1, 1],
                [-1, 0],
                [-1, 1],
                [-1, 1],
                [-1, 1],
                [-1, 1],
                [-1, 1],
                [-1, 1],
                [-1, 1]
            ],
            4, # num games
            101,  # num rounds
            60) # timeout
    ]


class TrainerServer:
    def __init__(self):
        self.taskmaster = Taskmaster()

        self.playerSpaces = createPlayerSpaces(self.taskmaster)

        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobReq, self.on_request)
        self.client.register_callback(config.mqttTopicJobOutcome, self.on_outcome)
        self.client.connect()

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobReq)
        client.subscribe(config.mqttTopicJobOutcome)

    def on_request(self, client, topic, content):
        print("GOT GAME REQUEST", topic, content)
        next_job = self.taskmaster.get_next_job()
        target_id = client.guess_interlocutor_id(topic)
        client.send_message(next_job, config.mqttTopicJobRes, True, target_id)

    def on_outcome(self, client, topic, content):
        print("GOT OUTCOME", topic, content)
        self.taskmaster.handle_outcome(content)


if __name__ == "__main__":
    trainer = TrainerServer()
    trainer.client.mqttc.loop_forever()
