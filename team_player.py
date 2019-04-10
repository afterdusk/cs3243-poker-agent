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
MAX_POT_AMOUNT = 320*2

def parseTPWeights(*weights):
    # Parse ThetaPlayer weights
    if len(weights) == 1:
        weights = weights[0]
    #print(weights)
    lambda_w = []
    lambda_w.extend(weights[:5])
    lambda_w.append(weights[7]+weights[12])
    lambda_w.extend(weights[8:12])
    lambda_w.extend(4*[weights[5],])
    lambda_w.extend(4*[weights[6],])
    #print(len(lambda_w))
    return lambda_w

# The second successor to EpsilonPlayer, now considers raises wrt STREET
class TeamPlayer(BasePokerPlayer):

    # Static variable
    number_of_weights = 18
    PLAYERBASE = {}

    PLAYERBASE['megagreed'] = parseTPWeights((0.85901144,-0.007261118,0.0045653,0.005953146,-0.037009216,-0.275107076,-0.062463787,-0.031791646,0.577145867,0.043871836,-0.71042045,0.718634854,0.0198525,-0.014965))
    PLAYERBASE['fulc'] = (0.117994414,0.05,0.23,0.02,0,-0.3,0.175032389,-0.235125649,0.54,0.749183248,-0.073978396,-0.407671667,-0.372985906,-0.325279514,0.376030346,-0.044681863,-0.148404011,-0.043494767)
    lion_w = (0.472384782*2,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741*2,0.734561248,0,0)
    PLAYERBASE['lion'] = parseTPWeights(lion_w)
    call_w = (0.02778*2,-0.00688,-0.02755,0.052426,-0.2474,-0.34341,-0.09206,-0.11463,0.37808,-0.46699,-0.44921*2,0.577757,0,0)
    PLAYERBASE['callpolice'] = parseTPWeights(call_w)
    ascend_w = (0.45854458*2,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254*2,0.717262457,0,0)
    PLAYERBASE['ascend'] = parseTPWeights(ascend_w)
    PLAYERBASE['pride2'] = (0.41856,-0.04605,-0.0508,-0.07398,-0.10022,-0.07048,0.31181,-0.15511,-0.52646,0.70109,-0.36287,-0.48434,-0.42068,-0.28957,0.03635,-0.03503,-0.15601,-0.10615)

    def __init__(self, playernames):

        self.team = []
        for name in playernames:
            if name in self.PLAYERBASE:
                self.team.append(name)
                print(name + " added to the roster")
            else:
                print("Bad name. " +str(name) + " not in PLAYERBASE")

        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }
        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0
        self.my_index = 0
        self.my_stack = 0
        self.earnings_delta = float(0)
        self.num_rounds_passed = 0
        # Ratio of earnings delta over games played. I.e. Avg Net earning per round
        self.loss_threshold = 330
        self.greed_threshold = 1.1
        self.currentPlayer = 0
        self.initNameWeights(self.team[0])


    def initNameWeights(self, name):
        data = self.PLAYERBASE[name]
        # Weights for card + pot value
        self.payout_w = activation_functions.logistic(0, 1, 2, 0)(data[0])

        # Weight for current round. Each round has 1 weight
        i = 0
        self.opp_TRA = [0,0,0,0]
        self.my_TRA = [0,0,0,0]
        for street in self.STREET_DICT:
            # Bias
            self.STREET_DICT[street] = data[1+i]
            self.opp_TRA[i] = data[10+i]
            self.my_TRA[i] = data[14+i]
            i += 1

        # Overall
        self.overall_bias = data[5]

        # Thresholds
        self.raise_threshold = data[6]
        self.call_threshold = data[7]

        self.pot_w = data[8]
        self.hand_w = data[9]

        return self

    def linear_eval(self, hole_cards, community_cards, pot_amount):
        #print("linear", hole_cards, community_cards, pot_amount, self_raises, opp_raises)
        # Payout as a function of hole value and pot amount
        hand_str = self.evaluateHand(hole_cards, community_cards)
        payout_o = self.payout_w*(hand_str)*(pot_amount/MAX_POT_AMOUNT)
        hand_o = self.hand_w*hand_str
        pot_o = self.pot_w*(pot_amount/MAX_POT_AMOUNT)
        turn_o = self.STREET_DICT[self.current_street]
        raises_o = self.getRaiseEval()
        output =  hand_o + pot_o + payout_o + turn_o + raises_o + self.overall_bias
        # Activation bounds [-1, 1]
        return activation_functions.logistic(0, 2, 4, -1)(output)

    def make_move(self, valid_actions, hole, community, pot_amount):
        confidence = self.linear_eval(hole, community, pot_amount)
        valid_action_strings = list(map(lambda a: a['action'],valid_actions))

        if confidence > self.raise_threshold and "raise" in valid_action_strings:
            return "raise"

        if confidence > self.call_threshold and "call" in valid_action_strings:
            return "call"

        return "fold"

    def declare_action(self, valid_actions, hole_card, round_state):
        self.current_street = round_state['street']
        community_cards = round_state['community_card']
        pot_amount = round_state['pot']['main']['amount']
        self.my_index = round_state['next_player']
        smallblind_index = round_state['small_blind_pos']
        hist = self.parse_history(round_state['action_histories'], self.my_index == smallblind_index)
        self.recordHistory(hist)
        decision = self.make_move(valid_actions,hole_card,community_cards, pot_amount)

        if DEBUG:
            print "Decision made: ", decision
        return decision  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        # initalize stacks
        self.my_stack = game_info['rule']['initial_stack']
        self.num_rounds_passed = 0
        self.round_buffer = max(game_info['rule']['max_round']/25,20)
        self.earnings_delta = float(0)

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.initRound()


    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # Only call this when the round ends
        self.roundEndEvaluation(round_state)
        pass

    def roundEndEvaluation(self,round_state):
        stacks = self.get_stacks(round_state, self.my_index)
        new_my_stack = stacks[0]
        #print("new",new_my_stack,'old',self.my_stack)
        self.earnings_delta += (new_my_stack - self.my_stack)
        self.num_rounds_passed += 1
        ratio = float(self.earnings_delta)/float(self.num_rounds_passed)
        lossbool = self.earnings_delta < -self.loss_threshold
        greedbool = self.num_rounds_passed > self.round_buffer and ratio < self.greed_threshold
        swap = lossbool or greedbool

        if swap:
            print("DELTA",self.earnings_delta, "ROUNDS PLAYED",self.num_rounds_passed, "ratio",ratio)
            self.nextBetterPlayer()
            self.earnings_delta = 0
            self.num_rounds_passed = 0
        self.my_stack = new_my_stack

    def nextBetterPlayer(self):
        out = self.team[self.currentPlayer]
        self.currentPlayer += 1
        if self.currentPlayer == len(self.team):
            self.currentPlayer = 0
        playerName = self.team[self.currentPlayer]
        self.initNameWeights(playerName)

    def initRound(self):
        self.opp_raise_history = [0,0,0,0]
        self.my_raise_history = [0,0,0,0]
        self.my_raises = 0
        self.opp_raises = 0
        self.opp_bet = 0

    def getRaiseEval(self):
        eval = float(0)
        for i in range(len(self.opp_raise_history)):
            eval += self.opp_raise_history[i]*self.opp_TRA[i] + self.my_raise_history[i]*self.my_TRA[i]
        eval/=MAX_RAISES
        return eval

    def evaluateHand(self, hole_cards, common_cards):
        # print(self.old_street, self.current_street)
        NUM_SIMULATIONS = 400
        hole = [Card.from_str(c).to_id() for c in hole_cards]
        community = [Card.from_str(c).to_id() for c in common_cards]

        if not self.old_street == self.current_street:
            self.num_sims = float(0)
            # If value is not cached...
            self.old_street = self.current_street

            if len(common_cards) == 0:
                self.curr_card_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
            else:
                self.curr_card_wr = estimate_win_rate(NUM_SIMULATIONS, hole, community)
            self.num_sims += NUM_SIMULATIONS

        else:
            # Continue to simulate
            if len(common_cards) == 0:
                delta_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
            else:
                delta_wr = estimate_win_rate(NUM_SIMULATIONS, hole, community)

            self.curr_card_wr = (float(NUM_SIMULATIONS)*delta_wr + self.num_sims*self.curr_card_wr)/(NUM_SIMULATIONS + self.num_sims)
            self.num_sims += NUM_SIMULATIONS
        return self.curr_card_wr

    def recordHistory(self, history):
        my_bet_amt, my_raises, opp_bet_amt, opp_raises = history
        street_index = street_as_int(self.current_street)
        if opp_raises > self.opp_raises:
            self.opp_raises += 1
            diff = opp_bet_amt - self.opp_bet
            self.opp_bet = opp_bet_amt
            self.opp_raise_history[street_index] = self.opp_raise_history[street_index] + 1
        if my_raises > self.my_raises:
            self.my_raises += 1
            self.my_raise_history[street_index] = self.my_raise_history[street_index] + 1

    @staticmethod
    def get_stacks(state, my_index):
        my_stack = state['seats'][my_index]['stack']
        opp_stack = state['seats'][1-my_index]['stack']
        return my_stack, opp_stack

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


# End of player class

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

def setup_ai():
    players = ('callpolice','lion')
    return TeamPlayer(players)
