from __future__ import division
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.action_checker import *
from pypokerengine.engine.card import Card
from fast_monte_carlo import estimate_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.api.emulator import Emulator, Event
from pypokerengine.utils.game_state_utils import *
import win_rate_estimates
from time import sleep
import pprint
import random
import string
import activation_functions
import numpy

############# Constants #############
DEBUG = 0
MAX_RAISES = 4
SMALL_BLIND = 10
ANTE = 0
MAX_POT_AMOUNT = 320
NUM_PLAYERS = 2
MAX_ROUNDS = 1000
#####################################


class MinimaxV2Player(BasePokerPlayer):
    hand_strengths = {}
    
    # linear eval
    number_of_weights = 9

    # smart eval
    # number_of_weights = 50

    def __init__(self, weights):
       # self.weights = weights
       # if sum(1 for weight in self.weights if weight < 0) > 0:
       # self.weights = [(i + 1)/2 for i in self.weights]
       # weights = [random.uniform(-1, 1) for i in range(0,9)]
       self.init_weights(weights)
       self.starting_stack = -1

       self.emulator = Emulator()
       self.emulator.set_game_rule(NUM_PLAYERS, MAX_ROUNDS, SMALL_BLIND, ANTE)
       self.fold_count = 0
    
    def init_weights(self, data):
       self.street_weights = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }
       
       i = 1
       for street in self.street_weights:
           self.street_weights[street] = data[i]
           i += 1

       self.enemy_raise_weight = data[4]
       self.my_raise_weight = data[5]
       self.overall_bias = data[6]
       self.pot_weight = data[7]
       self.hand_weight = data[8]

    def declare_action(self, valid_actions, hole_card, round_state):
        game_state = restore_game_state(round_state)
        
        # retrieve useful information
        self.my_index = round_state['next_player']
        self.is_small_blind = self.my_index == round_state['small_blind_pos'] 
        if self.starting_stack == -1: self.starting_stack = round_state['seats'][self.my_index]['stack']
        self.current_street = round_state['street']

        my_uuid = round_state['seats'][round_state['next_player']]['uuid']
        for player in game_state['table'].seats.players:
            if player.uuid == my_uuid:
                # attach hole cards for our player
                game_state = attach_hole_card(game_state, my_uuid, map(Card.from_str, hole_card))
            else:
                game_state = attach_hole_card_from_deck(game_state, player.uuid)
        
        # calculate hand strength
        self.current_hand_strength = self.get_hand_strength(hole_card, round_state['community_card'])

        tree = MinimaxTree(self, game_state)
        decision, payoff = tree.minimax_decision()
        if decision == "fold": 
            self.fold_count += 1
        if DEBUG:
            print "Payoff: ", payoff
            print "Decision Made: ", decision
            print "fold_count: " + str(self.fold_count)
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
        my_amount_bet = SMALL_BLIND if is_small_blind else 2 * SMALL_BLIND
        enemy_amount_bet = SMALL_BLIND if not is_small_blind else 2 * SMALL_BLIND
        my_num_raises = 0
        enemy_num_raises = 0
        
        flat_list = []
        streets = ["preflop", "flop", "turn", "river"]
        for street in streets:
            if street in history:
                flat_list.extend(history[street])
        
        my_uuid = flat_list[0]['uuid'] if is_small_blind else flat_list[1]['uuid']
        for i in flat_list:
            if i['action'] == "SMALLBLIND" or i['action'] == "BIGBLIND":
                continue
            if i['uuid'] == my_uuid:
                my_amount_bet += i['paid']
                my_num_raises += (i['action'] == 'RAISE')
            else:
                enemy_amount_bet += i['paid']
                enemy_num_raises += (i['action'] == 'RAISE')
        return my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises

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
        hand_strengths = MinimaxV2Player.hand_strengths
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
        return node.is_terminal

    @staticmethod
    def eval(node, pot_amount, my_num_raises, enemy_num_raises):
        hand = node.agent.current_hand_strength * node.agent.hand_weight
        pot = pot_amount/MAX_POT_AMOUNT * node.agent.pot_weight
        
        
        turn = node.agent.street_weights[node.agent.current_street]
        my_confidence = my_num_raises/4 * node.agent.my_raise_weight
        enemy_confidence = enemy_num_raises/4 * node.agent.enemy_raise_weight

        output_arr = [hand, pot, turn, my_confidence, enemy_confidence, node.agent.overall_bias]
        output = hand + pot + turn + my_confidence + enemy_confidence + node.agent.overall_bias
        scaled_output = activation_functions.tanh(0, 1, 2/3, 0)(output)
        if DEBUG:
            print "=" * 100
            print output, "->", scaled_output
            print output_arr
        return scaled_output
        

    @staticmethod
    def smart_eval(agent, pot_amount, raises_made):
        data = [1, agent.current_hand_strength, pot_amount/MAX_POT_AMOUNT, raises_made/MAX_RAISES]
        
        n = [data, [0] * 5, [0] * 5, [0] * 1]
        
        # First layer
        n[1][0] = activation_functions.tanh(2, 0.5, 2 / 2, 0.5)(numpy.dot(agent.weights[0:4], n[0]))
        n[1][1] = activation_functions.tanh(2, 0.5, 2 / 2, 0.5)(numpy.dot(agent.weights[4:8], n[0]))
        n[1][2] = activation_functions.tanh(2, 0.5, 2 / 2, 0.5)(numpy.dot(agent.weights[8:12], n[0]))
        n[1][3] = activation_functions.tanh(2, 0.5, 2 / 2, 0.5)(numpy.dot(agent.weights[12:16], n[0]))
        n[1][4] = activation_functions.tanh(2, 0.5, 2 / 2, 0.5)(numpy.dot(agent.weights[16:20], n[0]))

        # Second layer
        n[2][0] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[20:25], n[1]))
        n[2][1] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[25:30], n[1]))
        n[2][2] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[30:35], n[1]))
        n[2][3] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[35:40], n[1]))
        n[2][4] = activation_functions.tanh(2.5, 0.5, 2 / 2.5, 0.5)(numpy.dot(agent.weights[40:45], n[1]))

        # Third layer
        n[3][0] = activation_functions.tanh(2.5, 1, 2 / 2.5, 0)(numpy.dot(agent.weights[45:50], n[2]))

        # Max
        return n[3][0]
    

    @staticmethod
    def utility(node):
        index = -1
        while 'round_state' not in node.events[index]:
            index -= 1
        histories = node.events[index]['round_state']['action_histories']
        pot_amount = node.events[index]['round_state']['pot']['main']['amount']/2
        
        # if either player has folded
        if node.has_folded:
            # stack_change = node.events[index]['round_state']['seats'][node.agent.my_index]['stack'] - node.agent.starting_stack
            # if DEBUG:
                # start = "start stack: {}".format(node.agent.starting_stack)
                # end = "end stack: {}".format(node.events[index]['round_state']['seats'][node.agent.my_index]['stack'])
                # print "node: ", str(node.id), ", ", start, ", ", end
            if node.is_max:
                # if node is max, it means the previous player (opponent) folded
                return pot_amount
            else:
                # if node is min, it means the previous player (myself) folded
                return - pot_amount

         
        my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises = node.agent.parse_history(histories, node.agent.is_small_blind)
        result = MinimaxTree.eval(node, pot_amount, my_num_raises, enemy_num_raises)
        payoff = result * pot_amount
        if DEBUG:
            print "node : {}\teval result: {}, payoff: {}, pot: {}".format(node.id, result, payoff, pot_amount)
        return payoff

    def __init__(self, agent, game_state):
        # root is always a max node
        self.root = MinimaxNode(agent, True, False, False, game_state)

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
                print "(action: {}, payoff: {})".format(action, utility)
        return best_action, best_utility


class MinimaxNode:
    def __init__(self, agent, is_max, is_terminal, has_folded, game_state, events=None, level=1):
        self.agent = agent
        self.is_max = is_max
        self.game_state = game_state
        self.is_terminal = is_terminal
        self.events = events
        self.has_folded = has_folded
        self.level = level
        self.id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6));

    def successors(self):
        successors = []
        if DEBUG: print "=" * 20 + "successors({})".format(self.id) + "=" * 20
        actions = [i['action'] for i in self.agent.emulator.generate_possible_actions(self.game_state)]
        # generate a child node for each action
        for action in actions:
            child = self.generate_child(action)
            successors.append((action, child))

        return successors

    def generate_child(self, action):
        new_state = self.game_state.copy()
        has_folded = action == "fold"
        is_terminal = False
        
        # apply_action WILL modify action if somehow it's not legal
        # e.g. trying to raise while you are out of cash will result in the action
        # being converted to a fold
        # This is an issue because the generate_possible_actions method will say
        # that a player can raise when in fact he does not have the $$ to.
        new_state, events = self.agent.emulator.apply_action(new_state, action)
        
        # if terminal event detected
        if events[-1]['type'] in [Event.GAME_FINISH, Event.ROUND_FINISH]: 
            is_terminal = True
            index = -2 if events[-1]['type'] == Event.GAME_FINISH else -1
            # check if any party as folded
            if events[index]['round_state']['seats'][0]['state'] == 'folded' or events[index]['round_state']['seats'][1]['state'] == 'folded':
                has_folded = True
        child_node = MinimaxNode(self.agent, not self.is_max, is_terminal, has_folded, new_state, events, self.level + 1)
        if DEBUG: 
            print "node: {}".format(self.id), "\t", str(self.level), "--", action, "--> ", str(self.level + 1), "\tnode: ", str(child_node.id)
        return child_node


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
