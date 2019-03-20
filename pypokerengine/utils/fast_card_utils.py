import random
from pypokerengine.engine.card import Card
import deuces

evaluator_d = deuces.Evaluator()
card_lookup_d = [str(Card.from_id(c)) for c in xrange(1, 53)]
card_lookup_d = [deuces.Card.new(c[1] + c[0].lower()) for c in card_lookup_d]

def estimate_hole_card_win_rate(nb_simulation, hole, community=[]):
    wins = 0
    hole_d = [card_lookup_d[c - 1] for c in hole]

    for _ in xrange(nb_simulation):
        community_sim = community + pick_unused_cards(5 - len(community), hole + community)
        opp_sim = pick_unused_cards(2, hole + community_sim)

        community_sim_d = [card_lookup_d[c - 1] for c in community_sim]
        opp_sim_d = [card_lookup_d[c - 1] for c in opp_sim]

        hole_score = evaluator_d.evaluate(community_sim_d, hole_d)
        opp_sim_score = evaluator_d.evaluate(community_sim_d, opp_sim_d)
        
        if hole_score >= opp_sim_score:
            wins += 1

    return float(wins) / nb_simulation

def pick_unused_cards(n, used):
    return random.sample([c for c in xrange(1, 53) if c not in used], n)
