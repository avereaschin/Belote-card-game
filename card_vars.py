from collections import namedtuple

# Creating a card deck  
ranks = [str(i) for i in range(7, 11)] + 'J, Q, K, A'.split(', ')
suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
card = namedtuple('card', ['Rank', 'Suit'])
deck = [card(rank, suit) for rank in ranks for suit in suits]

# Make changes to this copy of the deck
deck_dealing = deck[:]

# Declaration values. To be used when comparing declarations
decl_values = {'10, 10, 10, 10': 100,
               '10, J, Q': 20,
               '10, J, Q, K': 50,
               '10, J, Q, K, A': 100,
               '7, 8, 9': 20,
               '7, 8, 9, 10': 50,
               '7, 8, 9, 10, J': 100,
               '7, 8, 9, 10, J, Q': 100,
               '7, 8, 9, 10, J, Q, K': 100,
               '7, 8, 9, 10, J, Q, K, A': 100,
               '8, 9, 10': 20,
               '8, 9, 10, J': 50,
               '8, 9, 10, J, Q': 100,
               '8, 9, 10, J, Q, K': 100,
               '8, 9, 10, J, Q, K, A': 100,
               '9, 10, J': 20,
               '9, 10, J, Q': 50,
               '9, 10, J, Q, K': 100,
               '9, 10, J, Q, K, A': 100,
               '7, 7, 7, 7': 0,
               '8, 8, 8, 8': 0,
               '9, 9, 9, 9': 150,
               'A, A, A, A': 100,
               'J, J, J, J': 200,
               'J, Q, K': 20,
               'J, Q, K, A': 50,
               'K, K, K, K': 100,
               'Q, K': 20,
               'Q, K, A': 20,
               'Q, Q, Q, Q': 100}

# Card values
card_vals = {'trump': {'10': 10, '7': 0, '8': 0, '9': 14, 'A': 11, 'J': 20, 'K': 4, 'Q': 3}, 
             'standard':{'10': 10, '7': 0, '8': 0, '9': 0, 'A': 11, 'J': 2, 'K': 4, 'Q': 3}}

# Hierarchy of ranks. To be used for checking player declarations.
hierarchy_ = {}
for i, value in enumerate(['7', '8', '9', '10', 'J', 'Q', 'K', 'A'], 1):
    hierarchy_[value] = i