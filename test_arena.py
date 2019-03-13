from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from trainable_player import MyTrainablePlayer
from raise_player import RaisedPlayer
from weighted_player import WeightedPlayer

def play_game(agentOne, agentTwo, rounds):
    # Game Settings
    config = setup_config(max_round=rounds, initial_stack=3000, small_blind_amount=10)
    config.register_player(name="Player 1 ", algorithm=agentOne)
    config.register_player(name="Player 2 ", algorithm=agentTwo)
    game_result = start_poker(config, verbose=0)
    return game_result

def playBots(botOne, botTwo, n, rounds):
    print("Playing " + str(n) + " games of " + str(rounds) + " rounds")
    wincount = 0
    i = 0
    stackOne = 0
    stackTwo = 0
    while i < n:
        result = play_game(botOne.getPlayer(),botTwo.getPlayer(), rounds)
        # Counts winrate from botOne perspective
        if result['players'][0]['stack']>result['players'][1]['stack'] :
            wincount += 1
        i+=1
        stackOne += result['players'][0]['stack']
        stackTwo += result['players'][1]['stack']

    print("P1 stack vs P2 stack: ")
    print(str(stackOne) + " vs " + str(stackTwo))
    print("winrate: " + str(wincount*100/n) + "%")

    if stackOne > stackTwo:
        winner = botOne
        loser = botTwo
    else:
        winner = botTwo
        loser = botOne

    print(winner.filename + " wins!")
    winner.reward(loser)
    return loser.deward()


def trainBots(first,second, games, rounds):
    print("Currently Training: <" + first + "> vs <" + second + ">")
    agentOne = MyTrainablePlayer(first)
    agentTwo = MyTrainablePlayer(second)
    # THIS CONTROLS EACH MATCH
    return playBots(agentOne, agentTwo, games, rounds)
