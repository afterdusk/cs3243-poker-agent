from syncengine.client import Client
from syncengine.taskmaster import Taskmaster
import config

# Import player spaces here
import SERVER_david_playerspace as david_playerspace
import ljs_copy_david_playerspace as lj_playerspace
import botlympics as botlympics
from cma_player_space import CMAPlayerSpace
from cma2_player_space import CMA2PlayerSpace
from rrt_player_space import RRTPlayerSpace
from profile_player_space import ProfilePlayerSpace

def createPlayerSpaces(taskmaster):
    #botlympics.init(taskmaster)
    lj_playerspace.init(taskmaster, "300319_LJ_Training")
    david_playerspace.init(taskmaster, "0104_Theta_Board")

    #CMA2PlayerSpace(
    #   taskmaster,
    #   'epsilon_player_train_1',
    #   'EpsilonPlayer',
    #   [[-1, 1]] * 12,
    #   500,
    #   1000,
    #   60 * 2
    #)

    ProfilePlayerSpace(
        taskmaster,
        'epsilon_player_profile_1',
        'EpsilonPlayer',
        5,
        [[-1, 1]] * 12,
        10,
        1000,
        1000,
        50,
        1000,
        60 * 2)
      



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
