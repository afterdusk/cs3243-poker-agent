from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer
from theta_player import ThetaPlayer
from lambda_player import LambdaPlayer

#TODO:config the config as our wish
RGIO_W = (0.40077642,-0.022973634,-0.094166709,0.09965165,0.035324082,-0.197451808,-0.026212688,-0.018908599,0.323128337,-0.317679528,-0.630921615,0.337817059)
RGIO = EpsilonPlayer(RGIO_W)

zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

callw = (0.02778,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921,0.577757)
call_player = EpsilonPlayer(callw)
tcallw = (0.02778*2,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921*2,0.577757,0,0)
tcall_player = ThetaPlayer(tcallw)
Z = (0.472384782,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741,0.734561248)

zLion = EpsilonPlayer(Z)

G = (0.45854458,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254,0.717262457)
greedcaller = EpsilonPlayer(G)

erw = (-0.15475,0.00125,0.062,-0.07975,-0.19175,-0.2795,0.076,0.00625,0.5325,-0.49475,-0.31425,0.5175)
Plat = EpsilonPlayer(erw)
greed = Group23Player()

Omega2_w = (0.457895,-0.0253075,-0.01069,0.0101225,0.0025675,-0.35887,-0.08472,-0.10998,0.3922275,-0.1183975,-0.5474175,0.715655,0.0253325,-0.05307)
Omega2Ex_w = (0.457895,0.0253075,0.01069,0.0101225,0.0025675,-0.34587,-0.01472,-0.10998,0.3922275,-0.1183975,-0.5474175,0.7205655,0.0253325,-0.05307)

OmegaOG = (0.39834,-0.021305,-0.02627,0.029645,-0.013075,-0.30985,-0.06516,-0.09723,0.410035,-0.095695,-0.520825,0.78539,0.041705,-0.02993)
OmegaStable = (0.39334,-0.021305,-0.02627,0.029645,-0.013075,-0.29485,-0.06516,-0.09723,0.410035,-0.095695,-0.505825,0.72539,0.039705,-0.02993)
OmegaPlayer = (0.4634,-0.021305,-0.02627,0.029645,-0.013075,-0.34785,-0.06516,-0.09723,0.410035,-0.095695,-0.550825,0.71539,0.039705,-0.02993)
oEx = (0.44034,-0.021305,-0.02627,0.029645,-0.013075,-0.34085,-0.008,-0.09723,0.410035,-0.095695,-0.540325,0.72739,0.039705,-0.02993)
PRIDE = (0.48393,-0.0370925,-0.03515,0.0109875,-0.0227425,-0.350185,-0.0771,-0.07662,0.4209825,-0.1094175,-0.5335175,0.719145,0.0159975,-0.01311)
wrath_w1= (0.457495,-0.03758,-0.010125,-0.04319,-0.050635,-0.327235,-0.05119,-0.11063,0.420975,-0.08234,-0.54522,0.737925,-0.016405,0.04441)
wrath_ex= (0.515495,-0.03758,-0.010125,-0.04319,-0.050635,-0.2527235,-0.05119,-0.11063,0.420975,-0.08234,-0.59522,0.757925,-0.0159405,0.04441)
wrath = ThetaPlayer(wrath_ex)

megagreed_w = (0.85901144,-0.007261118,0.0045653,0.005953146,-0.037009216,-0.275107076,-0.062463787,-0.031791646,0.577145867,0.043871836,-0.71042045,0.718634854,0.0198525,-0.014965)
MEGAGREED = ThetaPlayer(megagreed_w)

lp_w = (0.7,0,0,0,0,0,0.5771,0.043872,-0.5,0.75,0,0,0,0,0,0,0,0)
lplayer = LambdaPlayer(lp_w)
tp = MEGAGREED
tp = lplayer
#tp = tcall_player #Theta version of Call9996
# tp = call_player
print("BEGIN")
print("TESTING Lambda")

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Raiseplayer", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=0)
print(game_result)
if game_result['players'][0]['stack'] < 20000: exit()
# game_result = start_poker(config, verbose=0)
# print(game_result)
# game_result = start_poker(config, verbose=0)
# print(game_result)
# exit()

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Ascend", algorithm = greedcaller)
game_result = start_poker(config, verbose=0)
print(game_result)
# exit()

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="ZLion", algorithm = zLion)
game_result = start_poker(config, verbose=0)
print(game_result)

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="CallPolice", algorithm=call_player)
game_result = start_poker(config, verbose=0)
print(game_result)

#config.register_player(name="RGIO", algorithm = RGIO)
#config.register_player(name="T_Call_Killer", algorithm = tCall)
#config.register_player(name="T_Call_Killer2", algorithm = tCall)
#config.register_player(name="CallPolice", algorithm=call_player)
#config.register_player(name="Gr33dy", algorithm = greed)
#config.register_player(name="ZLion", algorithm = zLion)
