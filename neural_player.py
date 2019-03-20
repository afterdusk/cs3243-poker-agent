from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from time import sleep
import math
import pprint
import activation_functions
import numpy
import win_rate_estimator

class NeuralPlayer(BasePokerPlayer):

    def __init__(self, weights):
        self.initWeights(weights)

    def initWeights(self, data):
        self.weights = data
        return self

    def calculateHandValue(self, hole_cards, common_cards):
        properHoleCards = []
        for c in hole_cards:
            properHoleCards.append(Card.from_str(c))
        if len(common_cards) == 0:
            return win_rate_estimator.estimates[properHoleCards[0].to_id() - 1][properHoleCards[1].to_id() - 1]

        properCommunityCards = []
        for c in common_cards:
            properCommunityCards.append(Card.from_str(c))
        
        monte_carlo_value = estimate_hole_card_win_rate(100, 2, properHoleCards, properCommunityCards)
        return monte_carlo_value

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
