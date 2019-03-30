from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer

#TODO:config the config as our wish
config = setup_config(max_round=1500, initial_stack=30000, small_blind_amount=10)

YRZX = (0.595468388,-0.458556594,0.690242738,-0.018122754,0.229223682,0.324028161,0.207622531,-0.532829859,-0.069627984,0.125704346,-0.083964584)
yr = WisePlayer(YRZX)
zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

callw = (-0.097629624,-0.015322028,-0.053460944,0.079522507,-0.25760026,-0.386826604,-0.062169782,-0.033438914,0.385211212,-0.463661391,-0.383216098,0.580381615)
call_player = EpsilonPlayer(callw)

Z = (0.472384782,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741,0.734561248)
zLion = EpsilonPlayer(Z)

G = (0.45854458,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254,0.717262457)
greedcaller = EpsilonPlayer(G)

erw = (-0.15475,0.00125,0.062,-0.07975,-0.19175,-0.2795,0.076,0.00625,0.5325,-0.49475,-0.31425,0.5175)
Plat = EpsilonPlayer(erw)
greed = Group23Player()


#config.register_player(name="CallPolice", algorithm=call_player)
#config.register_player(name="Gr33dy", algorithm = greed)
#config.register_player(name="ZWUP", algorithm = good_player)
config.register_player(name="ZLion", algorithm = zLion)
#config.register_player(name="GreedCaller", algorithm = greedcaller)
#config.register_player(name="FT2", algorithm=RaisedPlayer())


print("HELLO!!")

game_result = start_poker(config, verbose=0)
print(game_result)
