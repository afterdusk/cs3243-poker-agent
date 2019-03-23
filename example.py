from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from delta_player import DeltaPlayer

#TODO:config the config as our wish
config = setup_config(max_round=100, initial_stack=10000, small_blind_amount=10)

w = (-1,-1, 1, 0.5,0.1,0.1,0.1,-0.2,0.1,0.3)
zp = DeltaPlayer(w)
config.register_player(name="Delta PLAYER", algorithm=zp)
config.register_player(name="FT2", algorithm=RaisedPlayer())


print("HELLO!!")

game_result = start_poker(config, verbose=1)
print(game_result)
