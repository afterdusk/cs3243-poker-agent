from __future__ import division
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.poker_constants import PokerConstants
from pypokerengine.engine.action_checker import *
from pypokerengine.engine.card import Card
from pypokerengine.utils import card_utils as ceval
from fast_monte_carlo import estimate_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator
import win_rate_estimates
from time import sleep
import pprint
import time
import random
import activation_functions
import numpy

############# Constants #############
MAX_RAISES = 4
SMALL_BLIND = 10
DEBUG = 0
MAX_POT_AMOUNT = 320
#####################################


class SmartWarrior(BasePokerPlayer):
    hand_strengths = {}

    def __init__(self, weights):
       self.weights = weights
       # self.weights = [random.uniform(-1, 1) for i in range(0,50)]
       # self.init_weights(weights)
       self.current_hand_strength = 0

    def init_weights(self, weights):
       self.overall_bias = weights[0]
       self.card_weight = weights[1]
       self.pot_weight = weights[2]
       self.confidence_weight = weights[3]

    def declare_action(self, valid_actions, hole_card, round_state):
        if DEBUG:
            print round_state['action_histories']
            print "Street: ", round_state['street']
        my_index = round_state['next_player']
        my_state = round_state['seats'][my_index]
        enemy_index = 0 if round_state['next_player'] == 1 else 1
        enemy_state = round_state['seats'][enemy_index]
        
        my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises = self.parse_history(round_state['action_histories'], my_index == round_state['small_blind_pos'])
       
        my_moves = self.get_valid_moves(my_state['stack'],
                                        my_num_raises,
                                        round_state['street'],
                                        round_state['pot']['main']['amount'])
       
        enemy_moves = self.get_valid_moves(enemy_state['stack'],
                                           enemy_num_raises, 
                                           round_state['street'], 
                                           round_state['pot']['main']['amount'])
        
        # remove fold from enemy moves
        if "fold" in enemy_moves: enemy_moves.remove("fold")

        # calculate hand strength
        self.current_hand_strength = self.get_hand_strength(hole_card, round_state['community_card'])

        max_player = PlayerState(
            my_state['stack'], 
            my_amount_bet, 
            my_moves, 
            my_num_raises, 
            hole_card,
            False,
            False)
        
        min_player = PlayerState(
            enemy_state['stack'], 
            enemy_amount_bet,
            enemy_moves, 
            enemy_num_raises, 
            [],
            False,
            False)

        game = GameState(round_state['pot']['main']['amount'], 
            round_state['community_card'],
            round_state['street'])

        tree = MinimaxTree(self, max_player, min_player, game)
        decision, payoff = tree.minimax_decision()
        if 1:
            print "Decision made: ", decision
        return decision  # action returned here is sent to the poker engine

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
    def parse_history(history, is_small_blind):
        my_turn = is_small_blind
        my_amount_bet = SMALL_BLIND if is_small_blind else 2 * SMALL_BLIND
        enemy_amount_bet = SMALL_BLIND if not is_small_blind else 2 * SMALL_BLIND
        my_num_raises = 0
        enemy_num_raises = 0
        flat_list = [i for street in history.values() for i in street]
        for i in flat_list:
            if DEBUG: print i
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

    @staticmethod
    def get_valid_moves(amount_left, num_raises, street, pot_amount):
        raise_amount, raise_limit = ActionChecker.round_raise_amount(SMALL_BLIND, street_as_int(street))
        if (num_raises >= MAX_RAISES or 
            pot_amount >= raise_limit or  # TODO: check this condition
            amount_left < raise_amount * 2):
            # raise_amount * 2 is generalisation, can still raise with less than that in reality
            return ["call", "fold"]
        return ["raise", "call", "fold"]

    @staticmethod
    def get_hand_strength(hole_cards, community_cards):
        # hand value via HandEvaluator 
        hole_cards = [Card.from_str(c) for c in hole_cards]
        community_cards = [Card.from_str(c) for c in community_cards]
        hand = HandEvaluator.eval_hand(hole_cards, community_cards)
        
        # hand strength via fast_card_utils monte carlo
        hole_cards = [c.to_id() for c in hole_cards]
        community_cards = [c.to_id() for c in community_cards]

        if len(community_cards) == 0:
            hand_strength = win_rate_estimates.estimates[hole_cards[0] - 1][hole_cards[1] - 1]
        else:
            hand_strength = estimate_win_rate(200, hole_cards, community_cards)
        
        # grab existing dict of hand strengths 
        hand_strengths = SmartWarrior.hand_strengths
        if hand in hand_strengths:
            # augment calculated value with previously calculated values
            num_prev_sims = hand_strengths[hand][1]
            final_strength = (hand_strengths[hand][0] * num_prev_sims + hand_strength) / (num_prev_sims + 1)
            hand_strengths[hand] = (final_strength, num_prev_sims + 1)
            return final_strength
        else:
            hand_strengths[hand] = (hand_strength, 1)
            return hand_strength

class MinimaxTree:
    @staticmethod
    def max_value(node, alpha, beta):
        if MinimaxTree.terminal_test(node):
            return MinimaxTree.utility(node)

        best = float("-inf")
        for (action, state) in node.successors():
            best = max(best, MinimaxTree.min_value(state, alpha, beta))
            if best >= beta:
                if DEBUG: print "pruned best: {}".format(best)
                return best
            alpha = max(alpha, best)
        if DEBUG: print "best: {}".format(best)
        return best

    @staticmethod
    def min_value(node, alpha, beta):
        if MinimaxTree.terminal_test(node):
            return MinimaxTree.utility(node)

        best = float("inf")
        for (action, state) in node.successors():
            best = min(best, MinimaxTree.max_value(state, alpha, beta))
            if best <= alpha:
                if DEBUG: print "pruned best: {}".format(best)
                return best
            beta = min(beta, best)
        if DEBUG: print "best: {}".format(best)
        return best

    @staticmethod
    def terminal_test(node):
        # there should be no situation where both players fold
        assert(
            not (node.max_player_state.has_folded and node.min_player_state.has_folded))

        if (node.max_player_state.has_folded or node.min_player_state.has_folded):
            return True
        if len(node.max_player_state.valid_actions) == 0 and len(node.min_player_state.valid_actions) == 0:
            return True
        return False

    @staticmethod
    def eval(agent, hole_cards, community_cards, pot_amount, raises_made):
        payoff = agent.card_weight * agent.current_hand_strength +\
            agent.pot_weight * pot_amount/MAX_POT_AMOUNT +\
            agent.confidence_weight * raises_made/MAX_RAISES +\
            agent.overall_bias
        if DEBUG: print "eval: {}".format(payoff)
        return payoff
    
    @staticmethod
    def smart_eval(agent, hole_cards, community_cards, pot_amount, raises_made):
        data = [1, agent.current_hand_strength, pot_amount/MAX_POT_AMOUNT, raises_made/MAX_RAISES]
        
        n = [data, [0] * 5, [0] * 5, [0] * 1]
        
        # First layer
        n[1][0] = activation_functions.tanh(1.5, 0.5, 2 / 1.5, 0.5)(numpy.dot(agent.weights[0:4], n[0]))
        n[1][1] = activation_functions.tanh(1.5, 0.5, 2 / 1.5, 0.5)(numpy.dot(agent.weights[4:8], n[0]))
        n[1][2] = activation_functions.tanh(1.5, 0.5, 2 / 1.5, 0.5)(numpy.dot(agent.weights[8:12], n[0]))
        n[1][3] = activation_functions.tanh(1.5, 0.5, 2 / 1.5, 0.5)(numpy.dot(agent.weights[12:16], n[0]))
        n[1][4] = activation_functions.tanh(1.5, 0.5, 2 / 1.5, 0.5)(numpy.dot(agent.weights[16:20], n[0]))

        # Second layer
        n[2][0] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[20:25], n[1]))
        n[2][1] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[25:30], n[1]))
        n[2][2] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[30:35], n[1]))
        n[2][3] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[35:40], n[1]))
        n[2][4] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[40:45], n[1]))

        # Third layer
        n[3][0] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[45:50], n[2]))

        # Max
        return n[3]
    

    @staticmethod
    def utility(node):
        # if either player has folded
        if (node.max_player_state.has_folded):
            if DEBUG: print "fold: {}".format(- (node.max_player_state.amount_bet / MAX_POT_AMOUNT))
            return - (node.max_player_state.amount_bet / MAX_POT_AMOUNT)
        if (node.min_player_state.has_folded):
            if DEBUG: print "fold: {}".format((node.game_state.pot_amount - node.max_player_state.amount_bet) / MAX_POT_AMOUNT)
            return (node.game_state.pot_amount - node.max_player_state.amount_bet) / MAX_POT_AMOUNT

        return MinimaxTree.smart_eval(node.agent, 
                                node.max_player_state.hole_cards, 
                                node.game_state.community_cards, 
                                node.game_state.pot_amount,
                                node.min_player_state.raises_made)

    def __init__(self, agent, max_player_state, min_player_state, game_state):
        # root is always a max node
        self.root = MinimaxNode(agent, True, max_player_state,
                                min_player_state, game_state)

    def minimax_decision(self):
        best_utility = float('-inf')
        best_action = None
        alpha = float("-inf")
        results = []
        successors = self.root.successors()
        for (action, state) in successors:
            utility = MinimaxTree.min_value(state, alpha, float("inf"))
            if utility > best_utility:
                best_utility = utility
                best_action = action
            alpha = max(alpha, utility)
            results.append((action, utility))
        if True:
            for (action, utility) in results:
                if DEBUG:
                    print "(action: {}, payoff: {})".format(
                        constant_to_string(action), utility)
        return best_action, best_utility


class MinimaxNode:
    def __init__(self, agent, is_max, max_player_state, min_player_state, game_state):
        self.agent = agent
        self.is_max = is_max
        self.max_player_state = max_player_state
        self.min_player_state = min_player_state
        self.game_state = game_state

    def successors(self):
        successors = []
        actions = []
        if self.is_max:
            actions = self.max_player_state.valid_actions
        else:
            actions = self.min_player_state.valid_actions

        if DEBUG:
            print "=" * 100
            print "Current " + ("Max" if self.is_max else "Min") + " Node: "
            print "\tMax Player State:"
            print "\t" + self.max_player_state.print_state()
            print "\tMin Player State:"
            print "\t" + self.min_player_state.print_state()
            print "\tGame State:"
            print "\t" + self.game_state.print_state()
            print "Successors:"

        # generate a child node for each action
        for action in actions:
            child_node = self.generate_successor(action)

            if DEBUG:
                print constant_to_string(action) + ": {"
                print "\tMax Player State:"
                print "\t" + child_node.max_player_state.print_state()
                print "\tMin Player State:"
                print "\t" + child_node.min_player_state.print_state()
                print "\tGame State:"
                print "\t" + child_node.game_state.print_state()
                print "}"
            successors.append((action, child_node))

        if DEBUG:
            print "=" * 100
        return successors

    def generate_successor(self, action):
        # copy states
        new_max_player_state = self.max_player_state.copy()
        new_min_player_state = self.min_player_state.copy()
        new_game_state = self.game_state.copy()
        # update states based on action performed
        if self.is_max:
            new_max_player_state.perform(action, new_game_state, new_min_player_state)
        else:
            new_min_player_state.perform(action, new_game_state, new_max_player_state)
        return MinimaxNode(self.agent, not self.is_max, new_max_player_state, new_min_player_state, new_game_state)

class PlayerState:
    
    def __init__(self, amount_left, amount_bet, valid_actions, raises_made, hole_cards, has_folded, has_played):
        self.amount_left = amount_left
        self.amount_bet = amount_bet
        self.valid_actions = valid_actions
        self.raises_made = raises_made
        self.hole_cards = hole_cards
        self.has_folded = has_folded
        self.has_played = has_played

    def perform(self, action, game_state, adversary_state):
        # raise amount and limit is constant for betting round, can move following call elsewhere to reduce
        # unnecessary calls
        raise_amount, raise_limit = ActionChecker.round_raise_amount(SMALL_BLIND, street_as_int(game_state.street))
        call_amount = adversary_state.amount_bet - self.amount_bet
        
        # you can only call by the amount you have left
        call_amount = min(call_amount, self.amount_left)
        
        if action == "fold":
            # a fold ends the round
            self.valid_actions = []
            adversary_state.valid_actions = []
            self.has_folded = True
            self.has_played = True
        elif action == "call":
            # only need to put in money if opponent has more in pot than you
            if call_amount > 0:
                assert (self.amount_left >= call_amount)
                self.amount_left -= call_amount
                self.amount_bet += call_amount
                game_state.pot_amount += call_amount
            self.has_played = True
            # a call ends the betting round if the opponent has played
            if (adversary_state.has_played):
                self.valid_actions = []
                adversary_state.valid_actions = []
        elif action == "raise":
            if call_amount > 0:
                assert(self.amount_left >= raise_amount + call_amount)
                self.amount_left -= raise_amount + call_amount
                self.amount_bet += raise_amount + call_amount
                game_state.pot_amount += raise_amount + call_amount
            else:
                self.amount_left -= raise_amount
                self.amount_bet += raise_amount
                game_state.pot_amount += raise_amount
            self.raises_made += 1
            self.has_played = True

        # remove raise if insufficient cash to raise later or if opp cannot match raise
        if "raise" in self.valid_actions and (self.raises_made >= MAX_RAISES or
                                              game_state.pot_amount >= raise_limit or  # TODO: check this condition
                                              self.amount_left < raise_amount * 2 or 
                                              adversary_state.amount_left < raise_amount):
            self.valid_actions.remove("raise")
        # remove call if unable to match opponent raise
        if "call" in self.valid_actions and self.amount_left < raise_amount:
            self.valid_actions.remove("call")
        # remove fold if only move left is fold
        if len(self.valid_actions) == 1 and self.valid_actions[0] == "fold":
            self.valid_actions.remove("fold")

    def copy(self):
        return PlayerState(self.amount_left,
                           self.amount_bet,
                           list(self.valid_actions),
                           self.raises_made,
                           list(self.hole_cards),
                           self.has_folded,
                           self.has_played)
    def print_state(self):
        return "amount_left: {}, amount_bet: {}, valid_actions: {}, raises_made: {}, hole_cards: {}".format(self.amount_left,
                                                                                                            self.amount_bet,
                                                                                                            map(constant_to_string, self.valid_actions),
                                                                                                            self.raises_made,
                                                                                                            self.hole_cards)

class GameState:
    def __init__(self, pot_amount, community_cards, street):
        self.pot_amount = pot_amount
        self.community_cards = community_cards
        self.street = street

    def copy(self):
        return GameState(self.pot_amount, list(self.community_cards), self.street)

    def print_state(self):
        return "pot_amount: {}, community_cards: {}, street: {}".format(self.pot_amount, self.community_cards, self.street)

def setup_ai():
    return SmartWarrior()

def street_as_int(street):
    street = street.lower()
    if street == "preflop":
        return 0
    if street == "flop":
        return 1
    if street == "turn":
        return 2
    if street == "river":
        return 3

def constant_to_string(constant):
    if constant == PokerConstants.Action.FOLD:
        return "Fold"
    elif constant == PokerConstants.Action.CALL:
        return "Call"
    elif constant == PokerConstants.Action.RAISE:
        return "Raise"
    return constant

def main():
    max_player = PlayerState(
        990, 
        10, 
        ["fold", "call", "raise"], 
        0, 
        ["C2", "C4"],
        False,
        False)

    min_player = PlayerState(
    980,
    20,
    ["call", "raise"], 
    0, 
    [],
    False,
    False)

    game = GameState(30, 
        ["H3", "C9", "S3", "S2", "H4"],
        "preflop")

    tree = MinimaxTree(SmartWarrior(), max_player, min_player, game)
    decision, payoff = tree.minimax_decision()
    if DEBUG:
        print "Decision made: ", decision

if __name__ == '__main__':
    main()
