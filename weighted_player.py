from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from time import sleep
import math
import pprint
import activation_functions

class WeightedPlayer(BasePokerPlayer):

    def __init__(self, weights):
        self.initWeights(weights)

    def initWeights(self, data):
        # The higher these value, the more conservative the play
        self.raise_threshold = activation_functions.logistic(0, 1, 4, 0)(data[0])
        self.call_threshold = activation_functions.logistic(0, 1, 4, 0)(data[1])

        # Multipliers
        self.card_weight = activation_functions.logistic(0, 2, 4, -1)(data[2])
        self.card_bias = activation_functions.logistic(0, 2, 4, -1)(data[3])

        # Flat biases
        self.pot_weight = activation_functions.logistic(0, 2, 4, -1)(data[4])
        self.pot_bias = activation_functions.logistic(0, 2, 4, -1)(data[5])
        return self

    def calculateHandValue(self, hole_cards, common_cards):
        properHoleCards = []
        for c in hole_cards:
            properHoleCards.append(Card.from_str(c))
        properCommunityCards = []
        for c in common_cards:
            properCommunityCards.append(Card.from_str(c))
        value = HandEvaluator.eval_hand(properHoleCards, properCommunityCards)

        # Massage the value to be [0-1]
        #adjvalue = (math.log(value,2)-14)/7  OLD FORMULA

        adjvalue = math.sqrt(math.sqrt(value))/37
        #print(str(value) + " " + str(adjvalue))
        return adjvalue

    def decide(self, holeValue, movesHistory,  pot_amount):
        return self.card_weight*(holeValue+self.card_bias) + self.pot_weight*(pot_amount/100+self.pot_bias)

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
        community_cards = round_state['community_card']
        cardValue = self.calculateHandValue(hole_card, community_cards)
        movesHistory = round_state['action_histories']
        pot_amount = round_state['pot']['main']['amount']

        return self.decideOnAction(valid_actions, cardValue, movesHistory, pot_amount)



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
        return MyPlayer()
