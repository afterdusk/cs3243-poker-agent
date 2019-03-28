from syncengine.client import Client
from syncengine.taskmaster import Taskmaster
import config

# Import player spaces here
import SERVER_david_playerspace as david_playerspace
import botlympics as botlympics
from cma_player_space import CMAPlayerSpace
from profile_player_space import ProfilePlayerSpace

def createPlayerSpaces(taskmaster):
    # Init player spaces here
    david_playerspace.init(taskmaster)
    # botlympics.init(taskmaster)
    
    CMAPlayerSpace(
        taskmaster,
        'neural3_player_train_apple',
        'Neural3Player',
        [[-1, 1]] * 10 + [[0, 1]] * 2,
        2500,
        4,
        101,
        60 * 4)
    
    ProfilePlayerSpace(
        taskmaster,
        'neural3_player_profile_apple',
        'Neural3Player',
        [[-1, 1]] * 10 + [[0, 1]] * 2,
        20,
        2500,
        1000,
        4,
        101,
        60 * 4)
   



class TrainerServer:
    def __init__(self, client_id=None):
        self.taskmaster = Taskmaster()

        self.playerSpaces = createPlayerSpaces(self.taskmaster)

        self.client = Client(client_id)
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
