from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.engine.card import Card

def estimate(hole_cards):                        
    return estimate_hole_card_win_rate(100000, 2, [Card.from_id(i) for i in hole_cards], [])

results = [[0] * 52] * 52
print(results)

for h1 in xrange(1, 53):
    for h2 in xrange(1, 53):
        if h1 == h2:
            win_rate = 0
        else:
            win_rate = estimate([h1, h2])
        print(h1, h2, win_rate)
        results[h1 - 1][h2 - 1] = win_rate

print(results)

