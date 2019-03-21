import csv
import random
import os
import activation_functions
#import win_rate_estimator
from pypokerengine.utils.fast_card_utils import estimate_hole_card_win_rate
# from fast_monte_carlo import estimate_hole_card_win_rate
from pypokerengine.engine.card import Card
from pypokerengine.players import BasePokerPlayer
from time import sleep

# Wise
class WisePlayer(BasePokerPlayer):

    # Static variable
    number_of_weights = 11

    def __init__(self, weights):
        print("INITALIZING WisePlayer")
        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }

        if len(weights) == self.number_of_weights:
            self.initWeights(weights)
        else:
            print("Bad number of weights. Expected " +str(self.number_of_weights) + " weights but got: " + str(weights))

        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0
        print("WisePlayer Created")

    def initWeights(self, data):
        # Decision thresholds
        self.raise_threshold = (data[0])
        self.call_threshold = (data[1])

        # Weights for card value
        self.card_weight = (data[2])

        # Weights for pot size
        self.pot_weight = (data[3])

        # Weight for current round
        i = 4
        for street in self.STREET_DICT:
            self.STREET_DICT[street] = data[i]
            i += 1

        # Weight for move history
        self.opp_raise_w = data[8]
        self.self_raise_w = data[9]

        # Overall
        self.overall_bias = data[10]

        return self

    def calculateHandValue(self, hole_cards, common_cards):
        hole = [Card.from_str(c).to_id() for c in hole_cards]
        community = [Card.from_str(c).to_id() for c in common_cards]
        # print(self.old_street, self.current_street)
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
        card_o = self.card_weight*(holeValue)
        pot_o = self.pot_weight*(pot_amount/320)
        turn_o = self.STREET_DICT[self.current_street]
        history_o = self.self_raise_w*raiseCounts[0] + self.opp_raise_w*raiseCounts[1]
        return card_o + pot_o + turn_o + history_o + self.overall_bias

    def decideOnAction(self, valid_actions, cardValue, movesHistory, pot_amount):
        confidence = self.decide(cardValue, movesHistory, pot_amount)
        valid_action_strings = list(map(lambda a: a['action'],valid_actions))
        if confidence > self.raise_threshold and "raise" in valid_action_strings:
            return "raise"

        if confidence > self.call_threshold and "call" in valid_action_strings:
            return "call"

        return "fold"

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
