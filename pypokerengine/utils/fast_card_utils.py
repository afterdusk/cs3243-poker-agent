import random
from pypokerengine.engine.card import Card
import deuces
import numpy as np

deck = np.array(range(1, 53))
evaluator_d = deuces.Evaluator()
card_lookup_d = [str(Card.from_id(c)) for c in deck]
card_lookup_d = [deuces.Card.new(c[1] + c[0].lower()) for c in card_lookup_d]

def estimate_hole_card_win_rate(nb_simulation, hole, community=np.ubyte([])):
    wins = 0
    hole_d = [card_lookup_d[c - 1] for c in hole]
    unused = np.setdiff1d(deck, hole)
    unused = np.setdiff1d(unused, community)

    for _ in xrange(nb_simulation):
        community_sim = np.append(community, np.random.choice(unused, 5 - len(community), False))
        unused_sim = np.setdiff1d(unused, community_sim)
        opp_sim = np.random.choice(unused_sim, 2, False)

        community_sim_d = [card_lookup_d[c - 1] for c in community_sim]
        opp_sim_d = [card_lookup_d[c - 1] for c in opp_sim]

        hole_score = evaluator_d.evaluate(community_sim_d, hole_d)
        opp_sim_score = evaluator_d.evaluate(community_sim_d, opp_sim_d)
        
        if hole_score <= opp_sim_score:
            wins += 1

    return float(wins) / nb_simulation
