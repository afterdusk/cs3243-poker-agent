from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer
from theta_player import ThetaPlayer
from lambda_player import LambdaPlayer

def parseTPWeights(*weights):
    # Parse ThetaPlayer weights
    if len(weights) == 1:
        weights = weights[0]
    #print(weights)
    lambda_w = []
    lambda_w.extend(weights[:5])
    lambda_w.append(weights[7]+weights[12])
    lambda_w.extend(weights[8:12])
    lambda_w.extend(4*[weights[5],])
    lambda_w.extend(4*[weights[6],])
    #print(len(lambda_w))
    return lambda_w

#TODO:config the config as our wish
RGIO_W = (0.40077642,-0.022973634,-0.094166709,0.09965165,0.035324082,-0.197451808,-0.026212688,-0.018908599,0.323128337,-0.317679528,-0.630921615,0.337817059)
RGIO = EpsilonPlayer(RGIO_W)

zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
good_player = WisePlayer(zwup)

callw = (0.02778,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921,0.577757)
call_player = EpsilonPlayer(callw)
tcallw = (0.02778*2,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921*2,0.577757,0,0)
tcall_player = ThetaPlayer(tcallw)
LCALL = LambdaPlayer(parseTPWeights(tcallw))
Z = (0.472384782,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741,0.734561248)

zLion = EpsilonPlayer(Z)

G = (0.45854458,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254,0.717262457)
greedcaller = EpsilonPlayer(G)

erw = (-0.15475,0.00125,0.062,-0.07975,-0.19175,-0.2795,0.076,0.00625,0.5325,-0.49475,-0.31425,0.5175)
Plat = EpsilonPlayer(erw)
greed = Group23Player()

razorw = (0.438243, 0.004563,-0.07531,0.056285,-0.0606,-0.17443,-0.08682,0.01531,0.160619,-0.8632,-0.35054,0.181355)
Razor = EpsilonPlayer(razorw)

megagreed_w = (0.85901144,-0.007261118,0.0045653,0.005953146,-0.037009216,-0.275107076,-0.062463787,-0.031791646,0.577145867,0.043871836,-0.71042045,0.718634854,0.0198525,-0.014965)
MEGAGREED = ThetaPlayer(megagreed_w)

lp_w = (0.7,0,0,0,0,0,0.5771,0.043872,-0.5,0.75,0,0,0,0,0,0,0,0)
lplayer = LambdaPlayer(lp_w)
#tp = MEGAGREED

fulcw = (-0.117994414,-0.485044214,-0.503214145,-0.463887481,-0.484160035,0.18964434,0.175032389,-0.235125649,0.524988773,0.739183248,-0.123978396,-0.407671667,-0.372985906,-0.325279514,0.376030346,-0.044681863,-0.148404011,-0.043494767)
fulcw2 = (0.117994414,-0.45044214,-0.503214145,-0.463887481,-0.484160035,0.18964434,0.175032389,-0.235125649,0.524988773,0.739183248,-0.073978396,-0.407671667,-0.372985906,-0.325279514,0.376030346,-0.044681863,-0.148404011,-0.043494767)
gdplay = LambdaPlayer(fulcw2)
rw = (0.4,0.05,0.05,-0.05,-0.05,0,-0.8,-0.8,0,0.5,0,0,0,0,0,0,0,0)
lraise = LambdaPlayer(rw)

tp = gdplay

print("BEGIN")
print("TESTING Lambda")

config = setup_config(max_round=301, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Raiseplayer", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=0)
print(game_result)
if game_result['players'][0]['stack'] < 20000: exit()
# game_result = start_poker(config, verbose=0)
# print(game_result)
# game_result = start_poker(config, verbose=0)
# print(game_result)

config = setup_config(max_round=3000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Razor", algorithm = Razor)
game_result = start_poker(config, verbose=0)
print(game_result)

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
