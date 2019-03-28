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

class NeuralPlayer(BasePokerPlayer):

    def __init__(self, weights):
        self.initWeights(weights)

    def initWeights(self, data):
        self.weights = data
        return self

    def calculateHandValue(self, hole, community):
        hole = [Card.from_str(c).to_id() for c in hole]
        community = [Card.from_str(c).to_id() for c in community]
            
        if len(community) == 0:
            return win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
       
        return fast_monte_carlo.estimate_win_rate(100, hole, community)

    def evaluate_network(self, data):
        # Network:
        # 2 ([0, 1]^3)
        # 5 ([0, 1]^5)
        # 5 ([0, 1]^5)
        # 3 ([0, 1]^3)
        # Max (1, 2, 3)
        n = [data, [0] * 5, [0] * 5, [0] * 3]
        
        # First layer
        n[1][0] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[0:2], n[0]))
        n[1][1] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[2:4], n[0]))
        n[1][2] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[4:6], n[0]))
        n[1][3] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[6:8], n[0]))
        n[1][4] = activation_functions.tanh(1.5, 0.5, float(2) / 1.5, 0.5)(numpy.dot(self.weights[8:10], n[0]))

        # Second layer
        n[2][0] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[10:15], n[1]))
        n[2][1] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[15:20], n[1]))
        n[2][2] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[20:25], n[1]))
        n[2][3] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[25:30], n[1]))
        n[2][4] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[30:35], n[1]))

        # Third layer
        n[3][0] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[35:40], n[2]))
        n[3][1] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[40:45], n[2]))
        n[3][2] = activation_functions.tanh(2.5, 0.5, float(2) / 2.5, 0.5)(numpy.dot(self.weights[45:50], n[2]))

        # Max
        return numpy.argmax(n[3])
    
    def declare_action(self, valid_actions, hole_card, round_state):
        community_cards = round_state['community_card']
        cardValue = self.calculateHandValue(hole_card, community_cards)
        movesHistory = round_state['action_histories']
        pot_amount = round_state['pot']['main']['amount']

        result = ['fold', 'call', 'raise'][self.evaluate_network([cardValue, float(pot_amount) / 320])]
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
