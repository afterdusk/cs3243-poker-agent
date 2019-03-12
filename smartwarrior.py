from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.poker_constants import PokerConstants
from pypokerengine.engine.action_checker import *
from time import sleep
import pprint

############# Constants #############
MAX_RAISES = 4
SMALL_BLIND = 10
DEBUG = True
#####################################


class SmartWarrior(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        for i in valid_actions:
            if i["action"] == "raise":
                action = i["action"]
                return action  # action returned here is sent to the poker engine
        action = valid_actions[1]["action"]
        return action  # action returned here is sent to the poker engine

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


class MinimaxTree:
    @staticmethod
    def max_value(node, alpha, beta):
        if MinimaxTree.terminal_test(node):
            return MinimaxTree.utility(node)

        best = float("-inf")
        for (action, state) in node.successors():
            best = max(best, MinimaxTree.min_value(state, alpha, beta))
            if best >= beta:
                return best
            alpha = max(alpha, best)
        return best

    @staticmethod
    def min_value(node, alpha, beta):
        if MinimaxTree.terminal_test(node):
            return MinimaxTree.utility(node)

        best = float("inf")
        for (action, state) in node.successors():
            best = min(best, MinimaxTree.max_value(state, alpha, beta))
            if best <= alpha:
                return best
            beta = min(beta, best)
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
            return - node.max_player_state.amount_bet
        if (node.min_player_state.has_folded):
            return node.game_state.pot_amount - node.max_player_state.amount_bet

        # TODO: write actual evaluation function
        return node.game_state.pot_amount - node.max_player_state.amount_bet

    def __init__(self, max_player_state, min_player_state, game_state):
        # root is always a max node
        self.root = MinimaxNode(True, max_player_state,
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
        if DEBUG:
            for (action, utility) in results:
                print "(action: {}, payoff: {})".format(
                    constant_to_string(action), utility)
        return best_action, best_utility


class MinimaxNode:
    def __init__(self, is_max, max_player_state, min_player_state, game_state):
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
        return MinimaxNode(not self.is_max, new_max_player_state, new_min_player_state, new_game_state)

class PlayerState:
    def __init__(self, amount_left, amount_bet, valid_actions, raises_made, hole_cards):
        self.amount_left = amount_left
        self.amount_bet = amount_bet
        self.valid_actions = valid_actions
        self.raises_made = raises_made
        self.hole_cards = hole_cards
        self.has_folded = False

    def perform(self, action, game_state, adversary_state):
        # raise amount and limit is constant for betting round, can move following call elsewhere to reduce
        # unnecessary calls
        raise_amount, raise_limit = ActionChecker.round_raise_amount(SMALL_BLIND, game_state.street)
        call_amount = adversary_state.amount_bet - self.amount_bet

        if action == PokerConstants.Action.FOLD:
            # a fold ends the round
            self.valid_actions = []
            adversary_state.valid_actions = []
            self.has_folded = True
        elif action == PokerConstants.Action.CALL:
            assert (self.amount_left >= call_amount)
            self.amount_left -= call_amount
            self.amount_bet += call_amount
            game_state.pot_amount += call_amount
            # a call ends the betting round
            self.valid_actions = []
            adversary_state.valid_actions = []
        elif action == PokerConstants.Action.RAISE:
            assert(self.amount_left >= raise_amount + call_amount)
            self.amount_left -= raise_amount + call_amount
            self.amount_bet += raise_amount + call_amount
            game_state.pot_amount += raise_amount + call_amount
            self.raises_made += 1

        # remove raise if insufficient cash to raise later
        if PokerConstants.Action.RAISE in self.valid_actions and (self.raises_made >= MAX_RAISES or
                                                                  game_state.pot_amount >= raise_limit or  # TODO: check this condition
                                                                  self.amount_left < raise_amount * 2):
            self.valid_actions.remove(PokerConstants.Action.RAISE)
        # remove call if unable to match opponent raise
        if PokerConstants.Action.CALL in self.valid_actions and self.amount_left < raise_amount:
            self.valid_actions.remove(PokerConstants.Action.CALL)
        # remove fold if only move left is fold
        if len(self.valid_actions) == 1 and self.valid_actions[0] == PokerConstants.Action.FOLD:
            self.valid_actions.remove(PokerConstants.Action.FOLD)

    def copy(self):
        return PlayerState(self.amount_left,
                           self.amount_bet,
                           list(self.valid_actions),
                           self.raises_made,
                           list(self.hole_cards))

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


def main():
    # TODO: Valid actions for root node needs to be validated
    max_player = PlayerState(
        40, 10, [PokerConstants.Action.FOLD, PokerConstants.Action.CALL, PokerConstants.Action.RAISE], 0, [])
    min_player = PlayerState(
        40, 20, [PokerConstants.Action.FOLD, PokerConstants. Action.CALL, PokerConstants.Action.RAISE], 0, [])
    game = GameState(30, [], 0)
    tree = MinimaxTree(max_player, min_player, game)
    decision, payoff = tree.minimax_decision()
    print "Minimax Decision: " + constant_to_string(decision)
    print "Decision Payoff: " + str(payoff)


def constant_to_string(constant):
    if constant == PokerConstants.Action.FOLD:
        return "Fold"
    elif constant == PokerConstants.Action.CALL:
        return "Call"
    elif constant == PokerConstants.Action.RAISE:
        return "Raise"


if __name__ == '__main__':
    main()
