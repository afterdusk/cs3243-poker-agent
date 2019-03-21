from pypokerengine.api.game import setup_config, start_poker
# from david_player import DavidPlayer
# from weighted_player import WeightedPlayer
# from neural_player import NeuralPlayer
from wise_player import WisePlayer
from smartwarrior import SmartWarrior

# CLIENT SIDE
# This will be run on each thread aka each core processor.

# A buffered queue of bot matchups
match_queue = []

def add_matchup(new_matchup):
    match_queue.append(new_matchup)

def play_game(agent_one, agent_two, rounds):
    # Game Settings
    config = setup_config(max_round=rounds, initial_stack=10000, small_blind_amount=20)
    config.register_player(name=agent_one[0], algorithm=agent_one[1])
    config.register_player(name=agent_two[0], algorithm=agent_two[1])
    game_result = start_poker(config, verbose=0)
    return game_result

def play_bots(agent_one, agent_two, n, rounds):
    print("Playing " + str(n) + " games of " + str(rounds) + " rounds")
    wincount = 0
    i = 0
    stack_one = 0
    stack_two = 0
    while i < n:
        result = play_game(agent_one,agent_two, rounds)
        # Counts winrate from agent_one perspective
        if result['players'][0]['stack']>result['players'][1]['stack'] :
            wincount += 1
        i+=1
        stack_one += result['players'][0]['stack']
        stack_two += result['players'][1]['stack']

    print(agent_one[0] + " stack vs "+ agent_two[0] + " stack: ")
    print(str(stack_one) + " vs " + str(stack_two))
    print("winrate: " + str(wincount*100/n) + "%")

    if stack_one > stack_two:
        winner = agent_one
        loser = agent_two
        result = 1
    else:
        winner = agent_two
        loser = agent_one
        result = 0

    print(winner[0] + " wins!")

    # returns 1 if first is the winner and 0 if the second is winner
    return result

# w is a tuple of weights
PLAYER_LIBRARY = {}
PLAYER_LIBRARY['DavidPlayer'] = lambda w: DavidPlayer(w)
PLAYER_LIBRARY['WeightedPlayer'] = lambda w: WeightedPlayer(w)
PLAYER_LIBRARY['NeuralPlayer'] = lambda w: NeuralPlayer(w)
PLAYER_LIBRARY['WisePlayer'] = lambda w: WisePlayer(w)
PLAYER_LIBRARY['SmartWarrior'] = lambda w: SmartWarrior(w)

# A job is {{bot1,bot2}, {training_regime}, {...extra info...}}
# Each bot is in a tuple of {bot_type, weights}
# training_regime is a tuple of {num_games, num_rounds per game}
def train_bots(matchup_job):
    first_bot, second_bot = matchup_job[0]
    training_regime = matchup_job[1]
    extra = matchup_job[2]

    # Initialization of players happens here
    p1_name = "Player 1"
    if first_bot[0] == 'DavidPlayer' or first_bot[0] == 'WisePlayer':
        p1_name = extra[0]
    p2_name = "Player 2"
    if second_bot[0] == 'DavidPlayer' or second_bot[0] == 'WisePlayer':
        p2_name = extra[1]
    agent_one = [p1_name, PLAYER_LIBRARY[first_bot[0]](first_bot[1])]
    agent_two = [p2_name, PLAYER_LIBRARY[second_bot[0]](second_bot[1])]


    print("Currently Training: <" + p1_name + "> vs <" + p2_name + ">")

    games = training_regime[0]
    rounds = training_regime[1]
    return play_bots(agent_one, agent_two, games, rounds)

# ============================ MAIN FUNCTION ============================
if __name__ == "__main__":
    current_match = recieve_matchup()
    outcome = train_bots(current_match)
