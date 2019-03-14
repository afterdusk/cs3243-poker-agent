from pypokerengine.api.game import setup_config, start_poker
from sync_trainable_player import MySyncablePlayer
from weighted_player import WeightedPlayer

# CLIENT SIDE
# This will be run on each thread aka each core processor.

# A buffered queue of bot matchups
match_queue = []

def add_matchup(new_matchup):
    match_queue.append(new_matchup)

def play_game(agent_one, agent_two, rounds):
    # Game Settings
    agent_one_name = agent_one[0]
    agent_one_player = agent_one[1].getPlayer()
    agent_two_name = agent_one[0]
    agent_two_player = agent_two[1].getPlayer()

    config = setup_config(max_round=rounds, initial_stack=10000, small_blind_amount=20)
    config.register_player(name=agent_one_name, algorithm=agent_one_player)
    config.register_player(name=agent_two_name, algorithm=agent_two_player)
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

    print("P1 stack vs P2 stack: ")
    print(str(stack_one) + " vs " + str(stack_two))
    print("winrate: " + str(wincount*100/n) + "%")

    if stack_one > stack_two:
        winner = agent_one
        loser = agent_two
    else:
        winner = agent_two
        loser = agent_one
    print(winner[0] + " wins!")

    # returns names of winner and loser in that order
    return (winner[0],loser[0])


# Each bot is in a tuple of {bot_type, name, weights, stats}
# training_regime is a tuple of {num_games, num_rounds per game}
def train_bots(matchup_job):
    #print(matchup_job)
    first_bot, second_bot = matchup_job[0]
    training_regime = matchup_job[1]

    print("Currently Training: <" + first_bot[1] + "> vs <" + second_bot[1] + ">")

    # Initialization of players happens here
    if first_bot[0] == "MySyncablePlayer":
        agent_one = (first_bot[1], MySyncablePlayer(first_bot))
    if second_bot[0] == "MySyncablePlayer":
        agent_two = (second_bot[1], MySyncablePlayer(second_bot))

    games = training_regime[0]
    rounds = training_regime[1]
    return play_bots(agent_one, agent_two, games, rounds)

def recieve_matchup():
    # E-Liang pls
    pass
    # get matchup from internet?

# ============================ MAIN FUNCTION ============================
def main():
    #while True:
    current_match = recieve_matchup()
    outcome = train_bots(current_match)
    # E-Liang help here
    # return outcome somehow
