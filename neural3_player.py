from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
import fast_monte_carlo
from time import sleep
import math
from activation_functions import tanh
import numpy
import win_rate_estimates

MAX_RAISES = 4
MAX_POT_AMOUNT = 320
STREET_NAMES = ['preflop', 'flop', 'turn', 'river']

class Neural3Player(BasePokerPlayer):

    def __init__(self, weights):
        self.initWeights(weights)

    def initWeights(self, data):
        self.weights = data
        return self

    def estimate_win_rate(self, hole, community):
        hole = [Card.from_str(c).to_id() for c in hole]
        community = [Card.from_str(c).to_id() for c in community]
            
        if len(community) == 0:
            return win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
        return fast_monte_carlo.estimate_win_rate(100, hole, community)
    
    # Adapted from SmartWarrior
    def get_raises(self, round_state):
        current_street_index = STREET_NAMES.index(round_state['street'])
        raises = 0
        opp_raises = 0

        history = round_state['action_histories']
        is_small_blind = round_state['next_player'] == round_state['small_blind_pos']
        is_player_turn = is_small_blind
        for street_index in xrange(current_street_index):
            street = history[STREET_NAMES[street_index]]
            for action in street:
                if action['action'] in ['SMALLBLIND', 'BIGBLIND']:
                    continue
                if is_player_turn:
                    raises += action['action'] == 'RAISE'
                else:
                    opp_raises += action['action'] == 'RAISE'
                is_player_turn = not is_player_turn
        
        return (raises, opp_raises)

    def evaluate_network(self, data):
        # Network structure
        n = [
            [0] * 9, 
            [0] * 6,
            [0] * 1]

        # Perception layer (9)
        n[0] = data
        
        # First layer (6)
        n[1][0] = numpy.dot(self.weights[0:4], n[0][0:4])
        n[1][1] = data[4]
        n[1][2] = data[5]
        n[1][3] = data[6]
        n[1][4] = data[7]
        n[1][5] = data[8]
    
        # Second layer (1)
        n[2][0] = numpy.dot(self.weights[4:10], n[1]) / 6
        
        if n[2][0] < -self.weights[10]:
            return 0 # Fold
        elif n[2][0] > self.weights[11]:
            return 2 # Raise
        else:
            return 1 # Call

    # Adapted from Epsilon Player, 2019-03-28 0116
    def declare_action(self, valid_actions, hole_card, round_state):
        community_cards = round_state['community_card']
        street = round_state['street']
        pot_amount = round_state['pot']['main']['amount']
        (raises, opp_raises) = self.get_raises(round_state)
        
        win_rate = self.estimate_win_rate(hole_card, community_cards)
        pot_amount_n = float(pot_amount) / MAX_POT_AMOUNT
        payout = win_rate * pot_amount_n
        is_preflop = street == 'preflop'
        is_flop = street == 'flop'
        is_turn = street == 'turn'
        is_river = street == 'river'
        (raises_n, opp_raises_n) = (float(raises) / MAX_RAISES, float(opp_raises) / MAX_RAISES)

        network_input = [
                is_preflop, 
                is_flop, 
                is_turn, 
                is_river,
                win_rate, 
                pot_amount_n, 
                payout, 
                raises_n, 
                opp_raises_n]

        result = ['fold', 'call', 'raise'][self.evaluate_network(network_input)]
        for act in valid_actions:
            if act['action'] == result:
                return act['action']
        return valid_actions[1]['action'] # fold

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def setup_ai():
        return Neural3Player()
