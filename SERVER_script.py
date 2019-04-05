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

    lj_playerspace.init(taskmaster, "050419_LJ_Training")
    david_playerspace.init(taskmaster, "0504_Lambda_Board")

    CMA2PlayerSpace(
        taskmaster,
        'theta_player_train_1',
        'ThetaPlayer',
        [[-1, 1]] * 14,
        20,
        1000,
        60 * 5)

    CMA2PlayerSpace(
        taskmaster,
        'theta_isolated_player_train_1',
        'ThetaIsolatedPlayer',
        [[-1, 1]] * 12,
        20,
        1000,
        60 * 5)

class TrainerServer:
    def __init__(self, client_id=None):
        self.taskmaster = Taskmaster()

        self.playerSpaces = createPlayerSpaces(self.taskmaster)

        self.client = Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.register_callback(config.mqttTopicJobReq, self.on_request)
        self.client.register_callback(config.mqttTopicJobOutcome, self.on_outcome)
        self.client.connect()

        self.client_ids = set()

    def on_connect(self, client):
        client.subscribe(config.mqttTopicJobReq)
        client.subscribe(config.mqttTopicJobOutcome)

    def on_request(self, client, topic, content):
        #  print("GOT GAME REQUEST", topic, content)
        next_job = self.taskmaster.get_next_job()
        target_id = client.guess_interlocutor_id(topic)
        if target_id not in self.client_ids:
            self.client_ids.add(target_id)
            print("NEW CLIENT", target_id, ". Num clients:", len(self.client_ids))
        client.send_message(next_job, config.mqttTopicJobRes, True, target_id)

    def on_outcome(self, client, topic, content):
        #  print("GOT OUTCOME", topic, content)
        self.taskmaster.handle_outcome(content)


if __name__ == "__main__":
    trainer = TrainerServer()
    trainer.client.mqttc.loop_forever()
