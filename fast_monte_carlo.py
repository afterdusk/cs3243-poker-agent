import OMPEval.omp_eval
from pypokerengine.engine.card import Card

lookup_rank = {
    '2': 0,
    '3': 1,
    '4': 2,
    '5': 3,
    '6': 4,
    '7': 5,
    '8': 6,
    '9': 7,
    'T': 8,
    'J': 9,
    'Q': 10,
    'K': 11,
    'A': 12
}

lookup_suit = {
    'D': 3,
    'C': 2,
    'H': 1,
    'S': 0
}

lookup = [str(Card.from_id(c)) for c in xrange(1, 53)]
lookup = [4 * lookup_rank[c[1]] + lookup_suit[c[0]] for c in lookup]

def estimate_win_rate(n_sim, hole, community=[]):
    hole_o = [lookup[c - 1] for c in hole]
    community_o = [lookup[c - 1] for c in community]

    return float(OMPEval.omp_eval.evaluate(n_sim, hole_o, community_o)) / n_sim
