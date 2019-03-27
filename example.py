from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer
from neural_player import NeuralPlayer

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=30000, small_blind_amount=10)

YRZX = (0.595468388,-0.458556594,0.690242738,-0.018122754,0.229223682,0.324028161,0.207622531,-0.532829859,-0.069627984,0.125704346,-0.083964584)
yr = WisePlayer(YRZX)
zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

callw = (-0.097629624,-0.015322028,-0.053460944,0.079522507,-0.25760026,-0.386826604,-0.062169782,-0.033438914,0.385211212,-0.463661391,-0.383216098,0.580381615)
call_player = EpsilonPlayer(callw)

erw = (0.438242914,0.004563298,-0.075314788,0.056284926,-0.06059732,-0.174429317,-0.086815867,0.015310329,0.160619342,-0.863199979,-0.350535249,0.181354672)
ERaise = EpsilonPlayer(erw)
greed = Group23Player()

NEURAL1W = (0.324591965,0.116853557,0.95764022,0.012027366,0.555069189,0.045179453,0.979426764,0.465743813,0.224603116,0.994112848,0.541695726,0.50800402,0.147543209,0.981098883,0.462406651,0.184512599,0.983589971,0.963924494,0.823646929,0.103798334,0.033531828,0.24722918,0.520595302,0.707991632,0.133658449,0.123737941,0.916372798,0.496648274,0.107323782,0.960525848,0.99767841,0.026340175,0.066576786,0.293650386,0.70985056,0.069822546,0.016017285,0.759767713,0.436462879,0.996274425,0.006816681,0.712753648,0.297351571,0.888931131,0.294428619,0.98731818,0.988812518,0.027874528,0.036252537,0.020522828
)

NEURAL = NeuralPlayer(NEURAL1W)

#config.register_player(name="Caller", algorithm=call_player)
config.register_player(name="Gr33dy", algorithm = greed)
config.register_player(name="ZWUP", algorithm = good_player)
#config.register_player(name="YRZX", algorithm = yr)
# config.register_player(name="Neural 1", algorithm = NEURAL)
# config.register_player(name="FT2", algorithm=RaisedPlayer())


print("HELLO!!")

game_result = start_poker(config, verbose=1)
print(game_result)
