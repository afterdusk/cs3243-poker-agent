import math
# from fast_monte_carlo import estimate_win_rate

from pypokerengine.engine.card import Card
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.poker_constants import PokerConstants
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate

# Fit for optimized estimate_win_rate
estimate_win_rate = lambda n, h, c: estimate_hole_card_win_rate(n, 2, h, c)

DEBUG = 0

# Game rules
SMALL_BLIND = 10
MAX_RAISES = 4
MAX_POT_AMOUNT = 320

# ACTIVATION FUNCTIONS
def logistic(center, scale, k, offset):
    return lambda x: float(scale) / (1 + math.exp(-k * (x - center))) + offset

def tanh(center, scale, k, offset):
    return lambda x: scale * math.tanh(k * (x - center)) + offset


class Group23Player(BasePokerPlayer):

    # Static variable
    number_of_weights = 12

    def __init__(self):
        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }
        self.weights = (0.62731144,0.006782764,0.0354006,-0.017738708,-0.060943432,-0.202364151,-0.059767574,0.033646709,0.744256733,0.183438671,-0.43500795,0.721879707)

        if len(self.weights) == self.number_of_weights:
            self.initWeights(self.weights)
        else:
            print("Bad number of weights. Expected " +str(self.number_of_weights) + " weights but got: " + str(weights))
            return 0

        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0

    def initWeights(self, data):
        # Decision thresholds

        # Weights for card + pot value
        self.payout_w = logistic(0, 1, 2, 0)(data[0])

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

            # hole = [Card.from_str(c).to_id() for c in hole_cards]
            # community = [Card.from_str(c).to_id() for c in common_cards]
            hole = [Card.from_str(c) for c in hole_cards]
            community = [Card.from_str(c) for c in common_cards]


            NUM_SIMULATIONS = 150
            if len(common_cards) == 0:
                #self.curr_card_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
                self.curr_card_wr = estimate_win_rate(NUM_SIMULATIONS, hole, [])
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
        return logistic(0, 2, 4, -1)(output)

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
        hist = self.parse_history(round_state['action_histories'], my_index == smallblind_index)
        my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises =  hist

        decision = self.make_move(valid_actions,hole_card,community_cards, pot_amount, my_num_raises, enemy_num_raises)



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
        return Group23Player()

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
