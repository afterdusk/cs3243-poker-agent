from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from wise_player import WisePlayer
from Group23Player import Group23Player
from epsilon_player import EpsilonPlayer
from theta_player import ThetaPlayer
from lambda_player import LambdaPlayer
from team_player import TeamPlayer
from minimaxv2player import MinimaxV2Player

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

# zwup = (0.547893555,-0.60075293,0.425702148,-0.061788086,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063)
# good_player = WisePlayer(zwup)

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
fulcw2 = (0.117994414,0.05,0.23,0.02,0,-0.3,0.175032389,-0.235125649,0.54,0.749183248,-0.073978396,-0.407671667,-0.372985906,-0.325279514,0.376030346,-0.044681863,-0.148404011,-0.043494767)
gdplay = LambdaPlayer(fulcw2)
rw = (0.4,0.05,0.05,-0.05,-0.05,0,-0.8,-0.8,0,0.5,0,0,0,0,0,0,0,0)
lraise = LambdaPlayer(rw)

pride2w = (0.41856,-0.04605,-0.0508,-0.07398,-0.10022,-0.07048,0.31181,-0.15511,-0.52646,0.70109,-0.36287,-0.48434,-0.42068,-0.28957,0.03635,-0.03503,-0.15601,-0.10615)
pride2wEX = (0.7756,0.12605,0.05,-0.03398,-0.05022,-0.08,0.31581,-0.15811,-0.43046,0.60109,-0.34587,-0.47434,-0.42068,-0.28957,0.03635,-0.03503,-0.15601,-0.10615)

prideV2 = LambdaPlayer(pride2w)

minmax_w = (0.405349021,0.045963426,0.169285631,0.127099172,-0.231639102,-0.126540016,-0.114880674,-0.045995445,0.800110469)
minmax = MinimaxV2Player(minmax_w)


G85w = (0.117685182,0.072886847,0.353819598,0.150551976,0.07052812,-0.163173705,0.827036618,0.279630331,0.080505841,0.914905221,-0.280973724,-0.639419401,-0.950301466,-0.494253437,0.577334089,0.386472439,0.347436493,-0.440368685)
test = (0.17685182,0.072886847,0.323819598,0.150551976,0.07052812,-0.163173705,0.827036618,0.229630331,-0.10505841,0.864905221,-0.230973724,-0.509419401,-0.78301466,-0.394253437,0.577334089,0.386472439,0.347436493,-0.440368685)
G85 = LambdaPlayer(G85w)

wrathsir_w = (0.297629292,0.049786245,0.122967539,0.08292289,-0.009234498,-0.117881087,0.635055951,0.109258146,-0.283136289,0.825488242,-0.261617786,-0.555953195,-0.592919143,-0.449949836,0.185070994,0.073960997,0.1608546,-0.270086074)
numsir_w = (0.124048855,0.112704493,0.274792076,0.162478695,0.036262792,-0.097084087,0.848983211,0.307150018,0.013884158,0.878733397,-0.215474327,-0.739364458,-0.858934594,-0.581222463,0.458913063,0.246341095,0.392669148,-0.480229021)
numsir2_w = (0.122996207,0.125085439,0.29225711,0.180102474,0.039180472,-0.121139926,0.857361954,0.323843001,0.014234181,0.881308427,-0.218497454,-0.667937497,-0.754606684,-0.573963344,0.448674516,0.226791482,0.394057881,-0.4692406)
wrathsir = LambdaPlayer(wrathsir_w)
numsir = LambdaPlayer(numsir2_w)

#tp = minmax
# tp = gdplay
# tp = prideV2
# tp = wrathsir
tp = TeamPlayer(('megagreed','pride2','callpolice','ascend'))

print("BEGIN")
print("TESTING Lambda")

config = setup_config(max_round=500, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Raiseplayer", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=0)
print(game_result)
# if game_result['players'][0]['stack'] < 20000: exit()
# game_result = start_poker(config, verbose=0)
# print(game_result)
# game_result = start_poker(config, verbose=0)
# print(game_result)

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Razor", algorithm = Razor)
game_result = start_poker(config, verbose=0)
print(game_result)

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="Ascend", algorithm = greedcaller)
game_result = start_poker(config, verbose=0)
print(game_result)
# exit()

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
config.register_player(name="Testing", algorithm = tp)
config.register_player(name="ZLion", algorithm = zLion)
game_result = start_poker(config, verbose=0)
print(game_result)

config = setup_config(max_round=1000, initial_stack=20000, small_blind_amount=10)
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
