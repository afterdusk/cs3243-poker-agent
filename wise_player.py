import csv
import random
import os
import activation_functions
#import win_rate_estimator
#from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.utils.fast_card_utils import estimate_hole_card_win_rate
from pypokerengine.engine.card import Card
from pypokerengine.players import BasePokerPlayer
from time import sleep

# Wise
class WisePlayer(BasePokerPlayer):

    # Static variable
    number_of_weights = 12

    def __init__(self, weights):
        print("INITALIZING")
        if len(weights) == self.number_of_weights:
            self.initWeights(weights)
        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0

    def initWeights(self, data):
        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }

        # The higher these value, the more conservative the play
        self.raise_threshold = activation_functions.logistic(0, 1, 4, 0)(data[0])
        self.call_threshold = activation_functions.logistic(0, 1, 4, 0)(data[1])

        # Weights for card value
        self.card_weight = activation_functions.logistic(0, 2, 4, -1)(data[2])
        self.card_bias = activation_functions.logistic(0, 2, 4, -1)(data[3])

        # Weights for pot size
        self.pot_weight = activation_functions.logistic(0, 2, 4, -1)(data[4])
        self.pot_bias = activation_functions.logistic(0, 2, 4, -1)(data[5])

        # Weight for current round
        for i in range(6,6+len(self.STREET_DICT)):
            print(i, data[i])
            self.street_weight = activation_functions.logistic(0, 2, 4, -1)(data[i])

        # Weight for move history
        self.opp_raise_w = data[10]
        self.self_raise_w = data[11]

        return self

    def calculateHandValue(self, hole_cards, common_cards):
        hole = [Card.from_str(c).to_id() for c in hole_cards]
        community = [Card.from_str(c).to_id() for c in common_cards]
        print(self.old_street, self.current_street)
        if not self.old_street == self.current_street:

            # If value is not cached...
            self.old_street = self.current_street
            NUM_SIMULATIONS = 100

            if len(common_cards) == 0:
                self.curr_card_wr = estimate_hole_card_win_rate(NUM_SIMULATIONS, hole)
                #return win_rate_estimator.estimates[properHoleCards[0] - 1][properHoleCards[1] - 1] COMMENT CUZ SLOW
            else:
                self.curr_card_wr = estimate_hole_card_win_rate(NUM_SIMULATIONS, hole, community)

        return self.curr_card_wr


    def decide(self, holeValue, raiseCounts,  pot_amount):
        card_o = self.card_weight*(holeValue+self.card_bias)
        pot_o = self.pot_weight*(pot_amount/320+self.pot_bias)
        turn_o = self.STREET_DICT[self.current_street]
        history_o = self.self_raise_w*raiseCounts[0] + self.opp_raise_w*raiseCounts[1]
        return card_o + pot_o + turn_o + history_o

    def decideOnAction(self, valid_actions, cardValue, movesHistory, pot_amount):
        confidence = self.decide(cardValue, movesHistory, pot_amount)
        if confidence > self.raise_threshold:
            for act in valid_actions:
                if act["action"] == "raise":
                    action = act["action"]
                    return action  # action returned here is sent to the poker engine

        elif confidence > self.call_threshold:
            for act in valid_actions:
                if act["action"] == "call":
                    action = act["action"]
                    return action  # action returned here is sent to the poker engine

        # Else fold
        action = valid_actions[1]["action"] #Fold
        return action # action returned here is sent to the poker engine

    def declare_action(self, valid_actions, hole_card, round_state):
        self.current_street = round_state['street']
        community_cards = round_state['community_card']
        holeValue = self.calculateHandValue(hole_card, community_cards)
        history = self.parse_history(round_state)
        raiseCounts = (history[1],history[3]) # Gets number of times raised
        pot_amount = round_state['pot']['main']['amount']

        return self.decideOnAction(valid_actions, holeValue, raiseCounts, pot_amount)

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

    @staticmethod
    def parse_history(round_state):
        SMALL_BLIND = 10
        history = round_state['action_histories']
        is_small_blind = round_state['next_player'] == round_state['small_blind_pos']
        my_turn = is_small_blind
        my_amount_bet = SMALL_BLIND if is_small_blind else 2 * SMALL_BLIND
        enemy_amount_bet = SMALL_BLIND if is_small_blind else 2 * SMALL_BLIND
        my_num_raises = 0
        enemy_num_raises = 0
        flat_list = [i for street in history.values() for i in street]
        for i in flat_list:
            if i['action'] == "SMALLBLIND" or i['action'] == "BIGBLIND":
                continue
            if my_turn:
                my_amount_bet += i['paid']
                my_num_raises += (i['action'] == 'RAISE')
            else:
                enemy_amount_bet += i['paid']
                enemy_num_raises += (i['action'] == 'RAISE')
            my_turn = not my_turn
        return my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises

    def setup_ai():
        return MyPlayer()
