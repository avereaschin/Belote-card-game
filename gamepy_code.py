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

print(card(Rank='J', Suit='Q'))

# screen setup
pg.init()

display_width, display_height = 1280, 720

game_display = pg.display.set_mode((display_width, display_height))
pg.display.set_caption('Belote')

#rgb codes
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 150, 0)
khaki = (240,230,140)

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
	print(card)
	return f'{card.Rank}_of_{card.Suit}.jpg'

class Card():

	surf_ = None
	rect_ = None
	card = None

	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

	def add_(self, x):
		self.card = x

	def create_surf(self):
		self.surf_ = pg.image.load(cardToFileName(self.card))


	def draw_rect(self):
		self.rect_ = self.create_surf().get_rect(topleft = (self.x, self.y))

class TestCard():

	def __init__(self, card_, x=0, y=0):
		self.card_ = card_
		self.x = x
		self.y = y
		self.surf = pg.image.load(cardToFileName(card_))
		self.rect = self.surf.get_rect(topleft = (x, y))

	def move(self):
		self.rect.y -= 20

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
	dict_ = {'you': 0, 'West': 0, 'North': 0, 'East': 0}

	def add_(self, player, points):
		self.dict_[player] = points
		
	def clear_(self):
		for key in list(self.dict_.keys()):
			dict_[key] = 0

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
	def __init__(self, text, size, x=0, y=0, bold=False, italic=False, color=black):

		self.text, self.size, self.x, self.y, self.color, self.bold, self.italic = text, size, x, y, color, bold, italic
		self.text_font = pg.font.SysFont('Arial', size, bold, italic)
		self.text_surf = pg.font.Font.render(self.text_font, text, False, color)
		self.text_rect = self.text_surf.get_rect()
		self.text_rect.topleft = (x, y)

	def set_topleft(self, x, y):
		self.text_rect.topleft = (x, y)

	def set_center(self, x, y):
		self.text_rect.center = (x, y)

class Hand():
    
    cards = []

    dict_ = {}

    def add_(self, x):
        if isinstance(x, list):
            self.cards = self.cards + x
        else:
            self.cards = self.cards + [x]
    
    def pop_(self, x):
        self.cards.pop(self.cards.index(x))

        
    def clear_(self):
        self.cards = []

    def make_dict(self):

    	self.dict_ = {k:[s,r,c] for k, s, r, c in zip(self.cards, self.create_surf(), self.draw_rect(), [None for i in range(len(self.cards))])}


    def create_surf(self):

    	return [pg.image.load(f'{card.Rank}_of_{card.Suit}.jpg') for card in self.cards]

    def draw_rect(self):
    	xy_coords = [(findMargin(self.cards) + (88 + 6) * i, display_height - 120) for i in range(len(self.cards))]

    	rects_ = [surf.get_rect() for surf in self.create_surf()]
    	for rect, xy in zip(rects_, xy_coords):
    		rect.topleft = xy

    	return rects_

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

cardback = Image('Francese_retro_Blu.jpg')
flip_cardback = pg.transform.rotate(cardback.image, 90)
score = Score() # keep track of player scores
sleep_ = Wait() # time.sleep substitute to be used in animations
rand_trump = Card()
hand = Hand() # holds YOUR cards
players = Players() # holds order in which players play cards
trump = ''

# upperleft x, y coords of each player's hand (except your own)
west_north_east = [(0, (display_height - 120) / 2), ((display_width - 88) / 2, 0), (display_width - 88, (display_height - 120) / 2)]

# during opponents turn this *thinking* cloud will appear above his name indicating he's thinking of a move
think_cloud = pg.transform.scale(pg.image.load('thought_bubble.png'), (50, 50))

think_cl_xy = {'West': [0, (49, display_height / 2 - 185)], 
			   'North': [1, ((display_width - 88 - 20 * 8) / 2 - 60 - 50, (120 - 20) / 2)], 
			   'East': [1, (display_width - 120 - 50, display_height / 2 - 185)]}

score_scr = pg.Surface((125, 100), pg.SRCALPHA)
score_scr.fill((255, 255, 255, 50))

def title_screen():
	
	crashed = False

	game_display.fill(white)

	print('TITLE: ', TextRender('start', 60, bold=True).text_rect.size)

	while not crashed:

		mx, my = pg.mouse.get_pos()	

		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True
			
			if event.type == pg.MOUSEBUTTONDOWN and start_b.collidepoint((mx, my)):
				return pickTrump()
		
		start_b = pg.draw.rect(game_display, black, [540, 620, 200, 100])

		game_display.blit(TextRender('start', 60, bold=True, color=white).text_surf, (575, 636)) # (129px, 68px)

		game_display.blit(TextRender('Belote', 115, bold=True).text_surf, (476, 240)) # (327px, 130px)


		pg.display.update()

def pickTrump():

	t1 = threading.Thread(target=main, daemon=True)
	t1.start()
	
	trump = ''
	msg = ''

	print('MSG ', TextRender('Passed', 25).text_rect.size)

	# Suit images
	files = ['Suit_Hearts.png', 'Suit_Diamonds.png', 'Suit_Clubs.png', 'Suit_Spades.png']

	suits_group = [resizeImage(pg.image.load(img), 50) for img in files]	
	suits_rect = [img.get_rect() for img in suits_group]
	
	for rect, xy in zip(suits_rect, [(420 + 8, 470 + 37), (420 + 58, 470 + 37), (420 + 116, 470 + 37), (420 + 174, 470 + 37)]):
		rect.topleft = xy

	s = pg.Surface((440, 100))
	s.fill((255, 255, 255, 255))

	crashed = False

	# Game states (changed accoording to instructions given by server)
	game_state = {'clients': None, 'round_1': False, 'round_2': False, 'round_2_must_pick': False, 'pick_trump': False, 'passed': False, 'o_pass': None, 
				  'o_think': False, 'trump': None, 'o_trump': None}
	
	# Key variables (changed accoording to instructions given by server)
	vars_ = {'hand 1': [(hand.add_, 1), (hand.create_surf, 0), (hand.draw_rect, 0)],
			'hand 2': [(hand.clear_, 0), (hand.add_, 1), (hand.make_dict, 0)],
			'clients': [(players.add_, 1), (players.sort_, 0)],
			'rand_trump': [(rand_trump.add_, 1), (rand_trump.create_surf, 0)]}

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
						trump = rand_trump.card.Suit
						game_state['pick_trump'] = True
						game_state['round_1'] = False
						clnt_q.put('play')

					# if clicked pass
					if pass_b.collidepoint((mx, my)):
						game_state['round_1'] = False
						game_state['passed'] = True
						clnt_q.put('pass')

				# on SECOND ROUND of picking trump
				if game_state['round_2']:	
					
					# if clicked on suit image
					for suit, rect in zip(suits_group, suits_rect):
						if rect.collidepoint((mx, my)):
							game_state['pick_trump'] = True
							game_state['round_2'] = False
							clnt_q.put(files[suits_group.index(suit)].split('_')[-1][:-4])
					# if clicked pass
					if pass_b.collidepoint((mx, my)):
						game_state['round_2'] = False
						clnt_q.put('pass')

				# on SECOND ROUND if YOU must pick a trump suit
				if game_state['round_2_must_pick']:
					# if clicked on suit image
					for suit, rect in zip(suits_group, suits_rect):
						if rect.collidepoint((mx, my)):
							clnt_q.put(files[suits_group.index(suit)].split('_')[-1][:-4])
							game_state['pick_trump'] = True
							game_state['round_2_must_pick'] = False

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


		# THINK CLOUD BLIT
		if game_state['o_think']:
			game_display.blit(pg.transform.flip(think_cloud, think_cl_xy[plyConvert(game_state['o_think'])][0], 0), think_cl_xy[plyConvert(game_state['o_think'])][1])

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
			game_display.blit(TextRender(f'Play {rand_trump.card.Suit} ?', 25).text_surf, ((display_width - TextRender(f'Play {rand_trump.card.Suit} ?', 25).text_rect.size[0])/2, 475))

			play_b = pg.draw.rect(game_display, black, (420 + 30, 470 + 40, 150, 33), 1)
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(TextRender('Play', 20).text_surf, (505, 514))
			game_display.blit(TextRender('Pass', 20).text_surf, (733, 514))

		# ROUND 2 BLIT 
		if game_state['round_2']:	
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(TextRender('Pick Trump Suit or Pass', 25).text_surf, (504, 472)) # (271px, 29px)
			
			# pass button blit
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(TextRender('Pass', 20).text_surf, (733, 514))

			# suits blit
			for suit, rect in zip(suits_group, suits_rect):
				game_display.blit(suit, rect)

		# ROUND 2 MUST PICK TRUMP BLIT 
		if game_state['round_2_must_pick']:	
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(TextRender('Everyone passed. You MUST pick a suit!', 20).text_surf, (460 , 475)) # (359px, 24px)
			
			for i, suit, rect in zip(range(4), suits_group, suits_rect):
				rect.x = 528 + 58 * i
				game_display.blit(suit, rect)
		
		# IF YOU PICKED TRUMP SUIT
		if game_state['pick_trump']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			s.blit(TextRender(f'You played {trump}', 25).text_surf, ((440 - TextRender(f'You played {trump}', 25).text_rect.size[0]) / 2, 2))
			if sleep_.wait_(1500):
				game_state['pick_trump'] = False
				declarations()


		# IF YOU PASSED
		if game_state['passed']:
			game_display.blit(TextRender('Passed', 25).text_surf, (597, 470)) # (85px, 29px)
			if sleep_.wait_(1500):
				game_state['passed'] = False

		# IF OPPONENT PASSED
		if game_state['o_pass']:
			game_display.blit(TextRender(f'{plyConvert(game_state["o_pass"])} passed', 25).text_surf, ((display_width - TextRender(f'{plyConvert(game_state["o_pass"])} passed', 25).text_rect.size[0]) / 2, 470))
			if sleep_.wait_(1500):
				game_state['o_pass'] = False

		# IF OPPONENT PICKED TRUMP SUIT
		if game_state['trump'] and game_state['o_trump']:
			game_display.blit(TextRender(f'{plyConvert(game_state["o_trump"])} picked {game_state["trump"]}', 25).text_surf, ((display_width - TextRender(f'{plyConvert(game_state["o_trump"])} picked {game_state["trump"]}', 25).text_rect.size[0]) / 2, 470))
			if sleep_.wait_(1500):
				game_state['o_trump'] = False
				declarations(game_state['trump'])
				
		pg.display.update()

def declarations(trump):

	decl_list = []
	declaration = []

	crashed = False	

	s = pg.Surface((440, 100))
	s.fill(white)

	# add declaration button
	add_s = pg.Surface((150, 33))
	add_s.fill(khaki)

	# clear declaration button
	clear_s = pg.Surface((150, 33))
	clear_s.fill(khaki)

	print('Declare: ', TextRender('Declare', 18).text_rect.size)
	print('No decl: ', TextRender('Nothing to declare', 20, bold=True).text_rect.size)

	game_state = {'any_decl': False, 'o_think': None, 'no_decl': False}

	while not crashed:
		
		# get variables and commands from message queue
		try:
			msg = q.get(False)	
		except queue.Empty:
			pass
		
		# process changes to game_state 
		if msg:
			game_state[msg[0]] = msg[1]

			# clear msg variable 
			msg = ''

		# background 
		game_display.fill(green)

		# get mouse x, y coordinates
		mx, my = pg.mouse.get_pos()

		# EVENT LOOP
		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True

			if event.type == pg.MOUSEBUTTONDOWN:
				
				for card in hand.cards:
					# if clicked on a card in YOUR hand
					if hand.dict_[card][1].collidepoint((mx, my)):
						# if card was not clicked before move it up by 20px
						if not hand.dict_[card][2]:
							hand.dict_[card][1].y -= 20
							hand.dict_[card][2] = True
							declaration.append(card)
							print(declaration)
						# if the card was clicked before (i.e. is already up 20px) move it down by 20px
						else:
							hand.dict_[card][1].y += 20
							hand.dict_[card][2] = None
							del declaration[declaration.index(card)]
							print(declaration)

				if game_state['any_decl']:
				
					# if pressed 'Declare' button send decl_list to server
					if play_b.collidepoint((mx, my)):
						clnt_q.put(decl_list)
					
					# if pressed 'No declarations' button send 'none' to server
					if pass_b.collidepoint((mx, my)):
						game_state['no_decl'] = True
						clnt_q.put('none')		
					
					# if pressed 'Add' button declaration to decl_list
					if add_d.collidepoint((mx, my)):
						decl_list += [declaration[:]]
						print(decl_list)
						declaration.clear()

						for card in hand.cards:
							if hand.dict_[card][2]:
								hand.dict_[card][1].y += 20 
								hand.dict_[card][2] = None

					# if pressed 'Clear' button clear decl_list and declaration variables
					if clear_d.collidepoint((mx, my)):
						decl_list.clear(), declaration.clear()

						print(declaration, decl_list)

						for card in hand.cards:
							if hand.dict_[card][2]:
								hand.dict_[card][1].y += 20 
								hand.dict_[card][2] = None 
				

		# DEFAULT SCORE BOARD
		game_display.blit(score_scr, (0, display_height - 100)) # (125px, 100px)
		
		score_scr.blit(TextRender('SCORES', 15).text_surf, (0, 0)) 
		
		for i, player, points in zip(range(4), score.dict_.keys(), score.dict_.values()):
			score_scr.blit(TextRender(f'{player}: {points}', 15).text_surf, (0, 20 + (12 + 4) * i))

		# DECLARATIONS PROMPT BLIT

		if game_state['any_decl']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 300))
			
			if game_state['no_decl']:
				s.blit(TextRender('Nothing to declare', 20, bold=True).text_surf, (133, 2)) # (174px, 24px)
				sleep_.wait_(1500)
				game_state['any_decl'] = False
				game_state['no_decl'] = False

			else:
				s.blit(TextRender('Any declarations?', 20, bold=True).text_surf, (141, 2)) # (157px, 24px)
				s.blit(TextRender('(Select cards, press add declaration then declare)', 17).text_surf, (37, 25)) # (365px, 20px)

				play_b = pg.draw.rect(game_display, black, (420 + 30, 475, 150, 33), 1)
				game_display.blit(TextRender('Declare', 18).text_surf, (420 + 30 + (150 - 62) / 2, 475 + (33 - 21) / 2)) # (62px, 21px)

				pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 475, 150, 33), 1)
				game_display.blit(TextRender('No declarations', 18).text_surf, (680 + (150 - 125) / 2, 475 + (33 - 21) / 2)) # (125px, 21px)

				game_display.blit(add_s, ((display_width - 320) / 2, display_height - 185))
				add_d = pg.draw.rect(game_display, black, ((display_width - 320) / 2, display_height - 185, 150, 33), 1)
				add_s.blit(TextRender('Add declaration', 16, italic=True).text_surf, (20, 7)) # (110px, 19px)

				game_display.blit(clear_s, ((display_width - 320) / 2 + 170, display_height - 185))
				clear_d = pg.draw.rect(game_display, black, ((display_width - 320) / 2 + 170, display_height - 185, 150, 33), 1)
				clear_s.blit(TextRender('Clear', 16, italic=True).text_surf, (56, 7)) # (38px, 19px)


		# THINK CLOUD BLIT
		if game_state['o_think']:
			game_display.blit(pg.transform.flip(think_cloud, think_cl_xy[plyConvert(game_state['o_think'])][0], 0), think_cl_xy[plyConvert(game_state['o_think'])][1])

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
		
		for card in hand.cards:
			game_display.blit(hand.dict_[card][0], hand.dict_[card][1])
		
		game_display.blit(example, (display_width - 120, display_height - 100))

		pg.display.update()



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



# declarations()
title_screen()



