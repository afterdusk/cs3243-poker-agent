from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer
from theta_player import ThetaPlayer

#TODO:config the config as our wish
RGIO_W = (0.40077642,-0.022973634,-0.094166709,0.09965165,0.035324082,-0.197451808,-0.026212688,-0.018908599,0.323128337,-0.317679528,-0.630921615,0.337817059)
RGIO = EpsilonPlayer(RGIO_W)

zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

callw = (0.02778,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921,0.577757)
call_player = EpsilonPlayer(callw)
Z = (0.472384782,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741,0.734561248)

tCall = ThetaPlayer(Z + (-0.012,-0.008))

zLion = EpsilonPlayer(Z)

G = (0.45854458,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254,0.717262457)
greedcaller = EpsilonPlayer(G)

erw = (-0.15475,0.00125,0.062,-0.07975,-0.19175,-0.2795,0.076,0.00625,0.5325,-0.49475,-0.31425,0.5175)
Plat = EpsilonPlayer(erw)
greed = Group23Player()

LionCall986 = (0.3842713004869657,-0.01859930416887775,-0.013721383027899842,0.03811035615974509,-0.032320079429710845,-0.3053368432978914,-0.0517824156436372,-0.055762478560196775,0.45731134247036587,-0.06214135361720763,-0.4876935328930009,0.7727753719244155,0.05577339838374313,-0.057029778385599195)
test = LionCall986
OmegaOG = (0.39834,-0.021305,-0.02627,0.029645,-0.013075,-0.30985,-0.06516,-0.09723,0.410035,-0.095695,-0.520825,0.78539,0.041705,-0.02993)
OmegaStable = (0.39334,-0.021305,-0.02627,0.029645,-0.013075,-0.29485,-0.06516,-0.09723,0.410035,-0.095695,-0.505825,0.72539,0.039705,-0.02993)
OmegaPlayer = (0.4634,-0.021305,-0.02627,0.029645,-0.013075,-0.34785,-0.06516,-0.09723,0.410035,-0.095695,-0.550825,0.71539,0.039705,-0.02993)
oEx = (0.44034,-0.021305,-0.02627,0.029645,-0.013075,-0.34085,-0.008,-0.09723,0.410035,-0.095695,-0.540325,0.72739,0.039705,-0.02993)
test = oEx
test2 = ()
tp = ThetaPlayer(test)

print("BEGIN")

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Raiseplayer", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=0)
print(game_result)
#exit()

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
#config.register_player(name="RGIO", algorithm = RGIO)
#config.register_player(name="T_Call_Killer", algorithm = tCall)
#config.register_player(name="T_Call_Killer2", algorithm = tCall)
#config.register_player(name="CallPolice", algorithm=call_player)
#config.register_player(name="Gr33dy", algorithm = greed)
#config.register_player(name="ZLion", algorithm = zLion)
config.register_player(name="Ascend", algorithm = greedcaller)
game_result = start_poker(config, verbose=0)
print(game_result)
# exit()

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="T_Call_Killer2", algorithm = tCall)
game_result = start_poker(config, verbose=0)
print(game_result)


config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="ZLion", algorithm = zLion)
game_result = start_poker(config, verbose=0)
print(game_result)

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="CallPolice", algorithm=call_player)
game_result = start_poker(config, verbose=0)
print(game_result)
