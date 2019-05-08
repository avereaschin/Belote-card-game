import pygame as pg
import os
import sys
from card_vars import ranks, suits, card, deck
import threading
from belote_client import q, main, clnt_q, sending
import queue
from random import choice

# path to game assets
os.chdir(r'Pics')

# screen setup
pg.init()

display_width, display_height = 1280, 720

game_display = pg.display.set_mode((display_width, display_height))
pg.display.set_caption('Belote')

#rgb codes
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 150, 0)

# holds all sprites
card_back = pg.sprite.Group()

# game state check for user exiting the game
crashed = False

def plyConvert(player):
	return players.dict_[player]

def resizeImage(pic, width):
	height = int(pic.get_rect().size[1] * width / pic.get_rect().size[1])
	return pg.transform.scale(pic, (width, height))

def findMargin(hand):
	"""
	Finds topleft x coord for the first card in a given hand in order to center it on the screen
	"""
	return (display_width / 2 - ((88 * len(hand) + 6 * (len(hand) - 1)) / 2))

def cardToFileName(card):
	return f'{card.Rank}_of_{card.Suit}.jpg'


class Card():

	card = ''
	surf_ = ''

	def add_(self, card_to_add):
		self.card = card_to_add

	def create_surf(self):
		self.surf_ = pg.image.load(cardToFileName(self.card))

class Players():

	list_ = []
	dict_ = {}

	def add_(self, players):
		self.list_ += players

	def sort_(self):
		order = self.list_[self.list_.index('you') + 1:] + self.list_[:self.list_.index('you')]  
		self.dict_ = {k:v for k, v in zip(order, ['West', 'North', 'East'])}

	def clear_(self):
		self.list_ = []
		self.dict_ = {}

class Score():
	"""
	Keeps track of player scores
	"""
	score_dict = {'you': 0, 'west': 0, 'north': 0, 'east': 0}

	def add_(self, player, points):
		self.score_dict[player] = points
		
	def clear_(self):
		for key in list(self.score_dict.keys()):
			score_dict[key] = 0

class Image():
	"""
	Creates a sprite by adding an image and creating a rect for it
	"""
	def __init__(self, pic, x=0, y=0, card=None):

		self.pic, self.x, self.y = pic, x, y
		self.image = pg.image.load(pic)
		split_ = lambda x: x.split('_')
		self.name = pic.split('_')[1][:-4]
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.card = card


class TextRender():
	def __init__(self, text, size, x=0, y=0, color = black):

		self.text, self.size, self.x, self.y, self.color = text, size, x, y, color
		self.text_font = pg.font.SysFont('Arial', size)
		self.text_surf = pg.font.Font.render(self.text_font, text, False, black)
		self.text_rect = self.text_surf.get_rect()
		self.text_rect.topleft = (x, y)

	def set_topleft(self, x, y):
		self.text_rect.topleft = (x, y)

	def set_center(self, x, y):
		self.text_rect.center = (x, y)

class Hand():
    
    cards = []
    
    
    def add_(self, x):
        if isinstance(x, list):
            self.cards = self.cards + x
        else:
            self.cards = self.cards + [x]
    
    def pop_(self, x):
        self.cards.pop(self.cards.index(x))
        
    def clear_(self):
        self.cards = []
        self.surf_ = None
        self.rect_ = None

    def create_surf(self):
    	return [pg.image.load(f'{card.Rank}_of_{card.Suit}.jpg') for card in self.cards]

    def draw_rect(self):
    	xy_coords = [(findMargin(self.cards) + (88 + 6) * i, display_height - 120) for i in range(len(self.cards))]

    	rects = [surf.get_rect() for surf in self.create_surf()]
    	for rect, xy in zip(rects, xy_coords):
    		rect.topleft = xy

    	return rects

class Wait():

	last = None

	def wait_(self, time_to_wait):	
		"""
		Returns True if time_to_wait ms have passed from last
		"""

		# to prevent repeatedly changing the last value with the wait method, the if statement checks if last has already been set
		if self.last == None:
			self.last = pg.time.get_ticks()

		now = pg.time.get_ticks()

		if self.last + time_to_wait <= now:
			self.last = None # clear last
			return True
		else:
			return False		

print('West size', TextRender('West', 25).text_rect.size)
print('North size', TextRender('North', 25).text_rect.size)

cardback = Image('Francese_retro_Blu.jpg')
flip_cardback = pg.transform.rotate(cardback.image, 90)

# time.sleep substitute to be used in animations
sleep_ = Wait()

rand_trump = Card()

# holds YOUR cards
hand = Hand()

# holds order in which players play cards
players = Players()

# upperleft x, y coords of each player's hand (except your own)
west_north_east = [(0, (display_height - 120) / 2), ((display_width - 88) / 2, 0), (display_width - 88, (display_height - 120) / 2)]

# during opponents turn this *thinking* cloud will appear above his name indicating he's thinking of a move
think_cloud = pg.transform.scale(pg.image.load('thought_bubble.png'), (50, 50))

def title_screen():
	
	crashed = False
	# message = ''

	game_display.fill(white)

	while not crashed:

		mx, my = pg.mouse.get_pos()	

		rect_drawing1 = pg.draw.rect(game_display, black, [(display_width / 2 - 100), display_height - 100, 200, 100])

		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True
			
			if event.type == pg.MOUSEBUTTONDOWN and rect_drawing1.collidepoint((mx, my)):
				return pickTrump()

		
		game_title = TextRender('Belote', 115, (display_width / 2), (display_height / 3))

		game_display.blit(game_title.text_surf, game_title.text_rect)


		pg.display.update()

def waitScreen(): 

	txt = TextRender('Joining game...', 80, display_width/2, display_height/3)
	to_wait = 0

	msg = ''

	game_display.fill(green)
	
	while True:
		
		for event in pg.event.get():
			if event.type == pg.QUIT:
				break
		try:
			msg = q.get(False)		
		except queue.Empty:
			pass

		if msg == 'start':
			game_display.blit(txt.text_surf, txt.text_rect)

			now = pg.time.get_ticks()
			msg = ''
			if pg.time.get_ticks() >= now + to_wait:
				print(now)
				return pickTrump()
				
		pg.display.update()

def pickTrump():

	t1 = threading.Thread(target=main, daemon=True)
	t1.start()
	
	# t2.start()
	trump = ''
	msg = ''

	# Suit images
	files = ['Suit_Hearts.png', 'Suit_Diamonds.png', 'Suit_Clubs.png', 'Suit_Spades.png']

	suits_group = [resizeImage(pg.image.load(img), 50) for img in files]	
	suits_rect = [img.get_rect() for img in suits_group]
	
	for rect, xy in zip(suits_rect, [(420 + 8, 470 + 37), (420 + 58, 470 + 37), (420 + 116, 470 + 37), (420 + 174, 470 + 37)]):
		rect.topleft = xy

	# Text lines
	txt = TextRender('Play Hearts?', 25)
	txt.set_topleft((display_width - txt.text_rect.size[0])/2, display_height - 245)

	t_trump2 = TextRender('Pick Trump Suit or Pass', 25)
	t_trump2.set_topleft(420 + (440 - t_trump2.text_rect.size[0]) / 2, 470 + 2)

	t_play = TextRender('Play', 20)
	t_play.set_topleft(420 + 30 + int((150 - 39) / 2), 470 + 40 + int((33 - 24) / 2))

	t_pass = TextRender('Pass', 20)
	t_pass.set_topleft(420 + 260 + int((150 - 44) / 2), 470 + 40 + int((33 - 24) / 2))

	text_dict = {'txt': TextRender('Play Hearts?', 25),
				't_trump2': TextRender('Pick Trump Suit or Pass', 25, 420 + (440 - t_trump2.text_rect.size[0]) / 2, 472),
				't_play': TextRender('Play', 20, 30 + int((150 - 39) / 2), 40 + int((33 - 24) / 2)),
				't_pass': TextRender('Pass', 20, 420 + 260 + int((150 - 44) / 2), 470 + 40 + int((33 - 24) / 2)),
				'score_w': TextRender('West: 0\nEast: 0\nNorth:0', 15, 0, 0),
				'passed': TextRender('Passed', 25)
				}

	print(text_dict['score_w'].text_rect.size)

	text_dict['score_w'].text = 'ahahah'
	# Important variables

	print(TextRender('Passed', 25).size)
	
	s = pg.Surface((440, 100))
	s.fill((255, 255, 255, 255))

	score_scr = pg.Surface((125, 100), pg.SRCALPHA)
	score_scr.fill((255, 255, 255, 50))

	crashed = False

	# Game states (changed accoording to instructions given by server)
	game_state = {'clients': None, 'round_1': False, 'round_2': False, 'pick_trump': False, 'passed': False, 'o_pass': None, 'o_play': False, 'trump': None, 'rand_trump': None, 'hand 1': None}
	
	# Key variables (changed accoording to instructions given by server)
	vars_ = {'hand 1': [(hand.add_, 1), (hand.create_surf, 0), (hand.draw_rect, 0)],
			'hand 2': [(hand.clear_, 0), (hand.add_, 1)],
			'clients': [(players.add_, 1), (players.sort_, 0)],
			'rand_trump': [(rand_trump.add_, 1), (rand_trump.create_surf, 0)]}

	print('size 5 letters is: ', TextRender('North', 25).text_rect.size)
	print('size 4 letters is: ', TextRender('East', 25).text_rect.size)
	print('size 1 letter is: ', TextRender('E', 25).text_rect.size)
	print('size 1 small letter: ', TextRender('e', 25).text_rect.size)
	print('size 2 small letters: ', TextRender('ea', 25).text_rect.size)
	print('size 4 small letters: ', TextRender('east', 25).text_rect.size)

	while not crashed:
		
		# get variables and commands from message queue
		try:
			msg = q.get(False)	
		except queue.Empty:
			pass
		
		# process messages and changes game_state vars_ accordingly
		if msg:
			# check if message is an instruction to change a variable
			if msg[0] in list(vars_.keys()):
				for instr in vars_[msg[0]]:
					# check if instruction needs to be called with an argument
					if instr[1]:
						instr[0](msg[1])
					# else call instruction without argument
					else:
						instr[0]()
			# else message is an instruction to change a game state value
			else:
				game_state[msg[0]] = msg[1]

			# clear msg variable 
			msg = ''


		# get mouse x, y coordinates
		mx, my = pg.mouse.get_pos()	

		# background 
		game_display.fill(green)
		
		# EVENT LOOP
		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True

			# on CLICK
			if event.type == pg.MOUSEBUTTONDOWN:
				
				# for surf, rect in zip(hand.create_surf(), hand.draw_rect()):
				# 	if rect.collidepoint((mx, my)):
				# 		print('True')

				# on FIRST ROUND of picking trump
				if game_state['round_1']:
					# if clicked play
					if play_b.collidepoint((mx, my)):
						clnt_q.put('play')
						trump = rand_trump.card.Suit
						text_dict['played_trump'] = TextRender(f'You played {trump}', 25, 420 + (440 - t_trump2.text_rect.size[0]) / 2, 470 + 2)
						game_state['pick_trump'] = True
						game_state['round_1'] = False

					# if clicked pass
					if pass_b.collidepoint((mx, my)):
						game_state['round_1'] = False
						game_state['passed'] = True
						clnt_q.put('pass')

				# on SECOND ROUND of picking trump
				if game_state['round_2']:	
					for suit, rect in zip(suits_group, suits_rect):
						# if clicked on suit image
						if rect.collidepoint((mx, my)):
							print(files[suits_group.index(suit)].split('_')[-1][:-4])
							trump = files[suits_group.index(suit)].split('_')[-1][:-4]
							clnt_q.put(trump)
							text_dict['played_trump'] = TextRender(f'You played {trump}', 25, 420 + (440 - t_trump2.text_rect.size[0]) / 2, 470 + 2)
					# if clicked pass
					if pass_b.collidepoint((mx, my)):
						clnt_q.put('pass')
						game_state['round_2'] = False

				# for i in hand_rect:
				# 	if i.collidepoint((mx, my)):
				# 		print(hand.cards[hand_rect.index(i)])

		# DEFAULT SCORE BOARD
		game_display.blit(score_scr, (0, display_height - 100)) # width, height = (125, 100)
		
		score_scr.blit(TextRender('SCORES', 15).text_surf, (0, 0)) 
		
		for i, player, score in zip([0, 1, 2, 3], ['you', 'west', 'north', 'east'], [0, 0, 0, 0]):
			score_scr.blit(TextRender(f'{player}: {score}', 15).text_surf, (0, 20 + (12 + 4) * i))

		# CARD BACK AND TRUMP BLIT (IF TRUMP HASN'T BEEN PICKED)
		if not game_state['trump']:
			game_display.blit(cardback.image, ((display_width - 88) / 2 + 15, (display_height - 120) / 2))
			if rand_trump.card:	
				game_display.blit(rand_trump.surf_, ((display_width - 88) / 2, (display_height - 120) / 2))


		# DEFAULT OPPONENT BLIT

		# west 
		game_display.blit(TextRender('West', 20).text_surf, (0, display_height / 2 - 154))
		
		for i in range(8):
			game_display.blit(flip_cardback, (0, (display_height - 88 - 20 * 8) / 2 + 20 * i))
		# north
		game_display.blit(TextRender('North', 20).text_surf, ((display_width - 88 - 20 * 8) / 2 - 60, (120 - 20) / 2))
		
		for i in range(8):
			game_display.blit(cardback.image, ((display_width - 88 - 20 * 8) / 2 + 20 * i, 0))

		# east
		game_display.blit(TextRender('East', 20).text_surf, (display_width - 120, display_height / 2 - 154))

		for i in range(8):
			game_display.blit(flip_cardback, (display_width - 120, (display_height - 88 - 20 * 8) / 2 + 20 * i))

		
		# DEFAULT YOUR CARDS BLIT 
		if hand.cards:
			for surf, rect in zip(hand.create_surf(), hand.draw_rect()):
				game_display.blit(surf, rect)

			
		# ROUND 1 BLIT
		if game_state['round_1']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(txt.text_surf, txt.text_rect)

			play_b = pg.draw.rect(game_display, black, (420 + 30, 470 + 40, 150, 33), 1)
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(t_play.text_surf, t_play.text_rect)
			game_display.blit(t_pass.text_surf, t_pass.text_rect)

		# ROUND 2 BLIT 
		if game_state['round_2']:	
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(t_trump2.text_surf, t_trump2.text_rect)
			
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(t_pass.text_surf, t_pass.text_rect)


			for suit, rect in zip(suits_group, suits_rect):
				game_display.blit(suit, rect)
		
		# IF YOU PICKED TRUMP SUIT
		if game_state['pick_trump']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(text_dict['played_trump'].text_surf, text_dict['played_trump'].text_rect)
			if sleep_.wait_(1500):
				game_state['pick_trump'] = False

		# IF YOU PASSED
		if game_state['passed']:
			game_display.blit(TextRender('Passed', 25).text_surf, (display_width / 2, 470))
			if sleep_.wait_(1500):
				game_state['passed'] = False

		# IF OPPONENT PASSED
		if game_state['o_pass']:
			game_display.blit(TextRender(f'{plyConvert(game_state["o_pass"])} passed', 25).text_surf, (display_width / 2, 470))
			if sleep_.wait_(1500):
				game_state['o_pass'] = False
				
		pg.display.update()

def declarations():

	crashed = False	

	# background 
	game_display.fill(green)

	while not crashed:
		
		# get mouse x, y coordinates
		mx, my = pg.mouse.get_pos()

		# EVENT LOOP
		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True

		# DEFAULT OPPONENT BLIT

		# west 
		game_display.blit(TextRender('West', 20).text_surf, (0, display_height / 2 - 154))
		
		for i in range(8):
			game_display.blit(flip_cardback, (0, (display_height - 88 - 20 * 8) / 2 + 20 * i))
		# north
		game_display.blit(TextRender('North', 20).text_surf, ((display_width - 88 - 20 * 8) / 2 - 60, (120 - 20) / 2))
		
		for i in range(8):
			game_display.blit(cardback.image, ((display_width - 88 - 20 * 8) / 2 + 20 * i, 0))

		# east
		game_display.blit(TextRender('East', 20).text_surf, (display_width - 120, display_height / 2 - 154))

		for i in range(8):
			game_display.blit(flip_cardback, (display_width - 120, (display_height - 88 - 20 * 8) / 2 + 20 * i))

		# DEFAULT YOUR CARDS BLIT 
		
		for surf, rect in zip(hand.create_surf(), hand.draw_rect()):
			game_display.blit(surf, rect)





def tricks():

	crashed = False
	# Card is clicked
	clicked = False
	# Card played
	played = False
	# Exit application
	

	game_display.fill(green)

	while not crashed:
		
		# get mouse x, y coordinates
		mx, my = pg.mouse.get_pos()				

		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True

		for j in range(0, 8):
			game_display.blit(pg.transform.rotate(cardback.image, 90), (0, int((display_height - 88 - 25*7) / 2 + 25 * j)))

		for j in range(0, 8):
			game_display.blit(cardback.image, (int((display_width - 88 - 25 * 7) / 2 + 25 * j), 0))

		for j in range(0, 8):
			game_display.blit(pg.transform.rotate(cardback.image, 90), (display_width - 120, int((display_height - 88 - 25*7) / 2 + 25 * j)))

		for i, j in zip(hand, xy_coords):	
			for k in suits_group:
				if i == k.name:
					game_display.blit(k.image, j)


		pg.display.update()

	pg.quit()
	quit()



title_screen()



