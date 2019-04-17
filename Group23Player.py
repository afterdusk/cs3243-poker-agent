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
MAX_POT_AMOUNT = 320*2
FOLD_QUEUE = 50

# ACTIVATION FUNCTIONS
def logistic(center, scale, k, offset):
    return lambda x: float(scale) / (1 + math.exp(-k * (x - center))) + offset

def tanh(center, scale, k, offset):
    return lambda x: scale * math.tanh(k * (x - center)) + offset


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


class Group23Player(BasePokerPlayer):

    # Static variable
    number_of_weights = 24

    def __init__(self):
        self.STREET_DICT = {'preflop':0, 'flop':0, 'river':0, 'turn':0 }
        self.my_index = 0
        self.weights = (0.412767608,0.054357942,0.077693212,0.077540568,-0.005489736,-0.075686809,0.625685788,0.147924773,-0.416736983,0.746136551,-0.242120234,-0.516898101,-0.503233478,-0.432802635,0.058118216,0.010455197,0.075981673,-0.284082785,-0.006853518,-0.017824961,-0.012240896,-0.026217108,-0.00401088,0.000853848)
        weights = self.weights
        if len(weights) == 18:
            #LambdaPlayer
            w2 = list(weights)
            ext = [0,0,0,0,0,0]
            w2.extend(ext)
            self.initWeights(w2)
            print("initalized extension")

        elif len(weights) == self.number_of_weights:
            self.initWeights(weights)
            # print("initalized normally")

        else:
            print("Bad number of weights. Expected " +str(self.number_of_weights) + " weights but got: " + str(len(weights)))
            exit()

        self.old_street = ""
        self.current_street = ""
        self.curr_card_wr = 0

    def initWeights(self, data):
        # Decision thresholds

        # Weights for card + pot value
        self.payout_w = logistic(0, 1, 2, 0)(data[0])

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

        self.b_aggro_w = data[18]
        self.c_aggro_w = data[19]
        self.b_thresh_w = data[20]
        self.c_thresh_w = data[21]
        self.fold_freq_thresh = data[22]
        self.fold_freq_bias = data[23]

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
        output = output + self.getAggroEval()
        # Activation bounds [-1, 1]
        if DEBUG:
            print(self.hand_w,hand_o,pot_o,payout_o,turn_o,raises_o,self.overall_bias)
            print(output, self.raise_threshold, self.call_threshold)
        return logistic(0, 2, 4, -1)(output)

    def make_move(self, valid_actions, hole, community, pot_amount):
        confidence = self.linear_eval(hole, community, pot_amount)
        if DEBUG:
            print("confidence",confidence)
        valid_action_strings = list(map(lambda a: a['action'],valid_actions))

        if confidence > self.raise_threshold and "raise" in valid_action_strings:
            return "raise"

        if confidence > self.call_threshold and "call" in valid_action_strings:
            return "call"

        self.countFold(1)
        return "fold"

    def declare_action(self, valid_actions, hole_card, round_state):
        self.current_street = round_state['street']
        community_cards = round_state['community_card']
        pot_amount = round_state['pot']['main']['amount']
        self.my_index = round_state['next_player']
        smallblind_index = round_state['small_blind_pos']
        hist = self.parse_history(round_state['action_histories'], self.my_index == smallblind_index)
        self.enemy_turns = hist[4]
        self.recordHistory(hist[:4])
        decision = self.make_move(valid_actions,hole_card,community_cards, pot_amount)

        if DEBUG:
            print "Decision made: ", decision
        return decision  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.initGame()

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.initRound()

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        self.recordAggro()
        self.countFold(0)
        self.rounds_elapsed += 1

    def recordAggro(self):
        if DEBUG:
            print("recording aggro")
            print(self.opp_raises,min(max(1,self.enemy_turns),MAX_RAISES))
        delta_aggro = float(self.opp_raises)/min(max(1,self.enemy_turns),MAX_RAISES)
        # print("raises",self.opp_raises,"/",self.enemy_turns,self.opp_aggro,"delta",delta_aggro)

        old_aggro = self.opp_aggro
        self.opp_aggro = (old_aggro*self.rounds_elapsed + delta_aggro)/(self.rounds_elapsed+1)


    def initRound(self):
        self.opp_raise_history = [0,0,0,0]
        self.my_raise_history = [0,0,0,0]
        self.my_raises = 0
        self.opp_raises = 0
        self.opp_bet = 0
        self.enemy_turns = 0

    def initGame(self):
        self.opp_aggro = float(0)
        self.rounds_elapsed = 1
        self.foldCount = [0]

    def getRaiseEval(self):
        eval = float(0)
        for i in range(len(self.opp_raise_history)):
            eval += self.opp_raise_history[i]*self.opp_TRA[i] + self.my_raise_history[i]*self.my_TRA[i]
        eval/=MAX_RAISES
        return eval

    def getAggroEval(self):
        def spread(val):
            return float(val)
            # val *= 10
            # return ((val-5)**3)/250 + 0.5

        def getFoldFreq():
            sum = 0
            for i in self.foldCount:
                sum+=i
            #print("FF", sum, self.foldCount)
            return float(sum)/len(self.foldCount)

        b_aggro_w = self.b_aggro_w
        bully_thresh = self.b_thresh_w*4.0

        c_aggro_w = self.c_aggro_w
        counter_thresh = self.c_thresh_w*4.0
        fold_freq = getFoldFreq()
        # print("Aggro val",self.opp_aggro)


        aggro_o = 0
        if self.opp_aggro > counter_thresh:
            aggro_o = c_aggro_w*spread(self.opp_aggro)
            #print("counter",fold_freq,self.opp_aggro,"final",aggro_o)

        elif self.opp_aggro < bully_thresh:
            aggro_o = b_aggro_w*spread((1-self.opp_aggro))

        if fold_freq > self.fold_freq_thresh:
            aggro_o += (1-fold_freq)*self.fold_freq_bias

        return aggro_o

    def countFold(self,fold):
        self.foldCount.insert(0,fold)
        if len(self.foldCount) > FOLD_QUEUE:
            self.foldCount.pop()

    def evaluateHand(self, hole_cards, common_cards):
        # print(self.old_street, self.current_street)
        NUM_SIMULATIONS = 200

        # Fast
        # hole = [Card.from_str(c).to_id() for c in hole_cards]
        # community = [Card.from_str(c).to_id() for c in common_cards]

        # Vanilla
        hole = [Card.from_str(c) for c in hole_cards]
        community = [Card.from_str(c) for c in common_cards]

        if not self.old_street == self.current_street:
            self.num_sims = float(0)
            # If value is not cached...
            self.old_street = self.current_street

            if len(common_cards) == 0:
                #self.curr_card_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
                self.curr_card_wr = estimate_win_rate(NUM_SIMULATIONS, hole, [])
            else:
                self.curr_card_wr = estimate_win_rate(NUM_SIMULATIONS, hole, community)
            self.num_sims += NUM_SIMULATIONS

        else:
            # Continue to simulate
            if len(common_cards) == 0:
                #delta_wr = win_rate_estimates.estimates[hole[0] - 1][hole[1] - 1]
                delta_wr = estimate_win_rate(NUM_SIMULATIONS, hole, [])
            else:
                delta_wr = estimate_win_rate(NUM_SIMULATIONS, hole, community)

            self.curr_card_wr = (float(NUM_SIMULATIONS)*delta_wr + self.num_sims*self.curr_card_wr)/(NUM_SIMULATIONS + self.num_sims)
            self.num_sims += NUM_SIMULATIONS
        return self.curr_card_wr

    def recordHistory(self, history):
        my_bet_amt, my_raises, opp_bet_amt, opp_raises = history
        street_index = street_as_int(self.current_street)
        if opp_raises > self.opp_raises:
            self.opp_raises = min(opp_raises,MAX_RAISES)
            diff = opp_bet_amt - self.opp_bet
            self.opp_bet = opp_bet_amt
            self.opp_raise_history[street_index] = self.opp_raise_history[street_index] + 1
        if my_raises > self.my_raises:
            self.my_raises = my_raises
            self.my_raise_history[street_index] = self.my_raise_history[street_index] + 1



# ====================== SMARTWARRIOR WORKINGS ====================== #

    @staticmethod
    def parse_history(history, is_small_blind):
        my_turn = is_small_blind
        my_amount_bet = SMALL_BLIND if is_small_blind else 2 * SMALL_BLIND
        enemy_amount_bet = SMALL_BLIND if not is_small_blind else 2 * SMALL_BLIND
        my_num_raises = 0
        enemy_num_raises = 0
        flat_list = [i for street in history.values() for i in street]
        enemy_turns = 0
        for i in flat_list:
            # if DEBUG: print i
            if i['action'] == "SMALLBLIND" or i['action'] == "BIGBLIND":
                continue
            if my_turn:
                my_amount_bet += i['paid']
                my_num_raises += (i['action'] == 'RAISE')
            else:
                enemy_turns += 1
                enemy_amount_bet += i['paid']
                enemy_num_raises += (i['action'] == 'RAISE')
            my_turn = not my_turn
        return my_amount_bet, my_num_raises, enemy_amount_bet, enemy_num_raises, enemy_turns

    @staticmethod
    def get_valid_moves(amount_left, num_raises, street, pot_amount):
        raise_amount, raise_limit = ActionChecker.round_raise_amount(SMALL_BLIND, street_as_int(street))
        if (num_raises >= MAX_RAISES or
            pot_amount >= raise_limit or  # TODO: check this condition
            amount_left < raise_amount * 2):
            # raise_amount * 2 is generalisation, can still raise with less than that in reality
            return ["call", "fold"]
        return ["raise", "call", "fold"]

def setup_ai():
    return Group23Player()
