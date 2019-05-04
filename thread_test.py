import queue
from card_vars import ranks, suits, card, deck
from random import choice


q = queue.Queue()
gp_q = queue.Queue()

# instructs = {'hand': Hand().add_, 'pick_trump': startGame}


def pickTrump(hand):
	pass

def startGame():
	q.put('start')

def inputFunc():
	for message in [['rand_card', card(Rank='Q', Suit='Hearts')], ['round_1', True]]:
		q.put(message)

	while 1:
		try:
			print(gp_q.get())
			break
		except queue.Empty:
			pass


	