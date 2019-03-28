import csv
import random
import os
import activation_functions
import win_rate_estimates
from fast_monte_carlo import estimate_win_rate
from pypokerengine.engine.card import Card
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.poker_constants import PokerConstants
from pypokerengine.players import BasePokerPlayer
from time import sleep

DEBUG = 0

# Game rules
SMALL_BLIND = 10
MAX_RAISES = 4
MAX_POT_AMOUNT = 320

# Delta sounds cool
class EpsilonPlayer(BasePokerPlayer):

    # Static variable
    number_of_weights = 12

    def __init__(self, weights):
        #print("INITALIZING WisePlayer")
        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }

        if len(weights) == self.number_of_weights:
            self.initWeights(weights)
        else:
            print("Bad number of weights. Expected " +str(self.number_of_weights) + " weights but got: " + str(weights))
            return 0

        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0

    def initWeights(self, data):
        # Decision thresholds

        # Weights for card + pot value
        self.payout_w = activation_functions.logistic(0, 1, 2, 0)(data[0])

        # Weight for current round. Each round has 1 weight
        i = 1
        for street in self.STREET_DICT:
            self.STREET_DICT[street] = data[i]
            i += 1

        # Weight for move history
        self.opp_raise_w = data[5]
        self.self_raise_w = data[6]

        # Overall
        self.overall_bias = data[7]

        # Thresholds
        self.raise_threshold = data[8]
        self.call_threshold = data[9]

        self.pot_w = data[10]
        self.hand_w = data[11]

        return self

    def evaluateHand(self, hole_cards, common_cards):
        # print(self.old_street, self.current_street)
        if not self.old_street == self.current_street:
            # If value is not cached...
            self.old_street = self.current_street

            hole = [Card.from_str(c).to_id() for c in hole_cards]
            community = [Card.from_str(c).to_id() for c in common_cards]

            NUM_SIMULATIONS = 150
            if len(common_cards) == 0:
                self.curr_card_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
            else:
                self.curr_card_wr = estimate_win_rate(NUM_SIMULATIONS, hole, community)

        return self.curr_card_wr

    def linear_eval(self, hole_cards, community_cards, pot_amount, self_raises, opp_raises):
        #print("linear", hole_cards, community_cards, pot_amount, self_raises, opp_raises)
        # Payout as a function of hole value and pot amount
        hand_str = self.evaluateHand(hole_cards, community_cards)
        payout_o = self.payout_w*(hand_str)*(pot_amount/MAX_POT_AMOUNT)
        hand_o = self.hand_w*hand_str
        pot_o = self.pot_w*(pot_amount/MAX_POT_AMOUNT)
        turn_o = self.STREET_DICT[self.current_street]
        history_o = (self.self_raise_w*self_raises/4) + (self.opp_raise_w*opp_raises/4)
        output =  hand_o + pot_o + payout_o + turn_o + history_o + self.overall_bias

        # Activation bounds [-1, 1]
        return activation_functions.logistic(0, 2, 4, -1)(output)

    def make_move(self, valid_actions, hole, community, pot_amount, my_raise, opp_raise):
        confidence = self.linear_eval(hole, community, pot_amount, my_raise, opp_raise)
        valid_action_strings = list(map(lambda a: a['action'],valid_actions))

        if confidence > self.raise_threshold and "raise" in valid_action_strings:
            return "raise"

        if confidence > self.call_threshold and "call" in valid_action_strings:
            return "call"

        return "fold"

    def declare_action(self, valid_actions, hole_card, round_state):
        self.current_street = round_state['street']
        # holeValue = self.calculateHandValue(hole_card, community_cards
        community_cards = round_state['community_card']
        pot_amount = round_state['pot']['main']['amount']
        my_index = round_state['next_player']
        smallblind_index = round_state['small_blind_pos']
        # my_state = round_state['seats'][my_index]
        # enemy_index = 1 - my_index
        # enemy_state = round_state['seats'][enemy_index]
        hist = self.parse_history(round_state['action_histories'], my_index == smallblind_index)
        my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises =  hist

        decision = self.make_move(valid_actions,hole_card,community_cards, pot_amount, my_num_raises, enemy_num_raises)

        # my_moves = self.get_valid_moves(my_state['stack'],
        #                                 my_num_raises,
        #                                 round_state['street'],
        #                                 round_state['pot']['main']['amount'])
        #
        # enemy_moves = self.get_valid_moves(enemy_state['stack'],
        #                                    enemy_num_raises,
        #                                    round_state['street'],
        #                                    round_state['pot']['main']['amount'])
        #
        # # remove fold from enemy moves
        # if "fold" in enemy_moves: enemy_moves.remove("fold")
        #
        # max_player = PlayerState(my_state['stack'], my_amount_bet,
        #     my_moves, my_num_raises, hole_card,False, False)
        #
        # min_player = PlayerState(enemy_state['stack'], enemy_amount_bet,
        #     enemy_moves, enemy_num_raises, [],False, False)
        #
        # game = GameState(round_state['pot']['main']['amount'],
        #     round_state['community_card'],
        #     round_state['street'])
        #
        # tree = MinimaxTree(self, max_player, min_player, game)
        # decision, payoff = tree.minimax_decision()


        if DEBUG:
        #if True:
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

    def setup_ai():
        return EpsilonPlayer()

# ====================== SMARTWARRIOR WORKINGS ====================== #

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

# End of player class

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
    def utility(node):
        # if either player has folded
        if (node.max_player_state.has_folded):
            if DEBUG: print "fold: {}".format(- (node.max_player_state.amount_bet / MAX_POT_AMOUNT))
            return - (node.max_player_state.amount_bet / MAX_POT_AMOUNT)
        if (node.min_player_state.has_folded):
            if DEBUG: print "fold: {}".format((node.game_state.pot_amount - node.max_player_state.amount_bet) / MAX_POT_AMOUNT)
            return (node.game_state.pot_amount - node.max_player_state.amount_bet) / MAX_POT_AMOUNT

        return node.agent.linear_eval(node.max_player_state.hole_cards,
                            node.game_state.community_cards,
                            node.game_state.pot_amount,
                            node.max_player_state.raises_made,
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


# UTILS

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
