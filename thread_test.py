import queue
from card_vars import ranks, suits, card, deck
from random import choice

rand_card = choice(deck)

q = queue.Queue()

def startGame():
	q.put('start')

def inputFunc():
	message = rand_card
	q.put(message)
	