from syncengine.client import Client
from syncengine.taskmaster import Taskmaster
import config

# Import player spaces here
import SERVER_david_playerspace as david_playerspace
import ljs_copy_david_playerspace as lj_playerspace
import botlympics as botlympics
from cma_player_space import CMAPlayerSpace
from rrt_player_space import RRTPlayerSpace
from profile_player_space import ProfilePlayerSpace

def createPlayerSpaces(taskmaster):
      #botlympics.init(taskmaster)
      lj_playerspace.init(taskmaster, "300319_LJ_Training")
      #david_playerspace.init(taskmaster, "3003_ChampPlat_Board")

      RRTPlayerSpace(
          taskmaster,
          'epsilon_player_train_apple',
          'EpsilonPlayer',
          [
              0.45854458,
              -0.010288565,
              0.023143473,
              0.003357603,
              -0.045208527,
              -0.291372468,
              0.012108953,
              -0.14727149,
              0.456158875,
              -0.156368715,
              -0.575275254,
              0.717262457
          ],
          [[-1, 1]] * 12,
          1,
          1000,
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
