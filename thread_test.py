import queue
from card_vars import ranks, suits, card, deck
from random import choice

rand_card = choice(deck)

q = queue.Queue()
clnt_q = queue.Queue()

# instructs = {'hand': Hand().add_, 'pick_trump': startGame}

# class Hand():
    
#     cards = []

#     # default_xy = # upperleft (x, y) coordinates for each card in hand
# 	# xy_coords = [(findMargin(hand) + (88 + 6) * i, display_height - 120) for i in range(len(hand))]
    
#     def add_(self, card):
#         if isinstance(x, list):
#             self.cards = self.cards + x
#         else:
#             self.cards = self.cards + [x]
    
#     def pop_(self, x):
#         self.cards.pop(self.cards.index(x))
        
#     def clear_(self):
#         self.cards = []

#     def create_surf(self):
#     	return [pg.image.load(f'{card.Rank}_of_{card.Suit}.jpg') for card in self.cards]

#     def draw_rect(self):
#     	return [surf.get_rect() for surf in self.create_surf()]

#     def set_xy(self, xy = None):
#     	xy = self.xy_coords if xy is None else xy 
#     	for rect, xy in (self.draw_rect(), xy):
#     		rect.topleft = xy


def pickTrump(hand):
	pass

def startGame():
	q.put('start')

def inputFunc():
	message = rand_card
	q.put(message)
	