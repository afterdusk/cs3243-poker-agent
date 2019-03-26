from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
import fast_monte_carlo
from time import sleep
import math
import pprint
import activation_functions
import numpy
import win_rate_estimates

STREET_NAMES = ['preflop', 'flop', 'turn', 'river']

class Neural2Player(BasePokerPlayer):

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
    
    def estimate_confidences(self, round_state):
        current_street_index = STREET_NAMES.index(round_state['street'])
        raise_counts = [0] * (current_street_index + 1)
        action_counts = [0] * (current_street_index + 1)

        history = round_state['action_histories']
        is_small_blind = round_state['next_player'] == round_state['small_blind_pos']
        is_player_turn = is_small_blind
        for street_index in xrange(current_street_index):
            street = history[STREET_NAMES[street_index]]
            for action in street:
                if action['action'] in ['SMALLBLIND', 'BIGBLIND']:
                    continue
                if not is_player_turn:
                    raise_counts[street_index] += action['action'] == 'RAISE'
                    action_counts[street_index] += 1
                is_player_turn = not is_player_turn
        
        raise_rates = []
        for (raise_count, action_count) in zip(raise_counts, action_counts):
            if action_count == 0:
                break
            raise_rates += [1 - float(raise_count) / action_count]
        return raise_rates

    def evaluate_network(self, data):
        # Network : Peception(3) -> 5 -> 7 -> 5 -> 3 -> Output(1)

        n = [[0] * 3, [0] * 5, [0] * 7, [0] * 5, [0] * 3]

        # Perception layer
        n[0][0] = data[0] # Pot amount
        n[0][1] = data[1] # Estimated win rate 
        if (data[2:] == []): # Estimated confidence
            n[0][2] = float(1)
        else:
            numerator = 0
            denominator = 0
            for (i, c) in enumerate(data[2:]):
                numerator += c * math.exp(self.weights[0] * i)
                denominator += math.exp(self.weights[0] * i)
            n[0][2] = float(numerator) / float(denominator)
        
        # First layer
        n[1][0] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[1:4], n[0]))
        n[1][1] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[4:7], n[0]))
        n[1][2] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[7:10], n[0]))
        n[1][3] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[10:13], n[0]))
        n[1][4] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[13:16], n[0]))

        # Second layer
        n[2][0] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[16:21], n[1]))
        n[2][1] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[21:26], n[1]))
        n[2][2] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[26:31], n[1]))
        n[2][3] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[31:36], n[1]))
        n[2][4] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[36:41], n[1]))
        n[2][5] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[41:46], n[1]))
        n[2][6] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[46:51], n[1]))

        # Third layer
        n[3][0] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[51:58], n[2]))
        n[3][1] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[58:65], n[2]))
        n[3][2] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[65:72], n[2]))
        n[3][3] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[72:79], n[2]))
        n[3][4] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[79:86], n[2]))
        

        # Fifth layer
        n[4][0] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[86:91], n[3]))
        n[4][1] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[91:96], n[3]))
        n[4][2] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[96:101], n[3]))

        # Output
        return numpy.argmax(n[4])
    
    def declare_action(self, valid_actions, hole_card, round_state):
        # Calculate normalized [0, 1] heuristics.
        community_cards = round_state['community_card']
        win_rate = self.estimate_win_rate(hole_card, community_cards)
        pot_amount = float(round_state['pot']['main']['amount']) / 320
        confidences = self.estimate_confidences(round_state)

        result = ['fold', 'call', 'raise'][self.evaluate_network([win_rate, pot_amount] + confidences)]
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
        return NeuralPlayer()
