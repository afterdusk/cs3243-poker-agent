from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from delta_player import DeltaPlayer
from epsilon_player import EpsilonPlayer

#TODO:config the config as our wish
config = setup_config(max_round=700, initial_stack=20000, small_blind_amount=10)

zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

hozz = (0.276658161,0.144486659,0.347482463,-0.222905572,-0.052651648,0.167400166,0.095893112,0.48666402,-0.131341578,-0.165388067,0.451192322,0.161379995)
zp = EpsilonPlayer(hozz)
config.register_player(name="ZWUP", algorithm = good_player)
#config.register_player(name="E-PLAYER", algorithm=zp)
config.register_player(name="FT2", algorithm=RaisedPlayer())


print("HELLO!!")

game_result = start_poker(config, verbose=0)
print(game_result)
