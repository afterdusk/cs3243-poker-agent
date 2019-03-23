from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from zair_player import ZairPlayer

#TODO:config the config as our wish
config = setup_config(max_round=10, initial_stack=10000, small_blind_amount=10)

w = (0.5,0.2,0.1,1,0.1,0.1,0.1,0.1,0.1,0.1)
zp = ZairPlayer(w)
config.register_player(name="ZAIR PLAYER", algorithm=zp)
config.register_player(name="FT2", algorithm=RaisedPlayer())


print("HELLO!!")

game_result = start_poker(config, verbose=1)
