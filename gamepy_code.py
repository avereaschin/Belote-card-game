import pygame as pg
import os
import time
from card_vars import ranks, suits, card, deck
import threading
from belote_client import q, main
import queue
from random import choice

# path to game assets
os.chdir(r'Pics')

# screen setup
pg.init()

display_width = 1280
display_height = 720

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

class Image():
	"""
	Creates a sprite by adding an image and creating a rect for it
	"""
	def __init__(self, pic, x=0, y=0):

		self.pic, self.x, self.y = pic, x, y
		self.image = pg.image.load(pic)
		split_ = lambda x: x.split('_')
		self.name = pic.split('_')[1][:-4]
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

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

    def create_surf(self):
    	return [pg.image.load(f'{card.Rank}_of_{card.Suit}.jpg') for card in self.cards]

    def draw_rect(self):
    	xy_coords = [(findMargin(self.cards) + (88 + 6) * i, display_height - 120) for i in range(len(self.cards))]

    	rects = [surf.get_rect() for surf in self.create_surf()]
    	for rect, xy in zip(rects, xy_coords):
    		rect.topleft = xy

    	return rects

    # def set_xy(self):
    # 	xy_coords = [(findMargin(self.cards) + (88 + 6) * i, display_height - 120) for i in range(len(self.cards))]
    	
    # 	# rect = self.draw_rect()

    # 	for rect, xy in zip(self.draw_rect(), xy_coords):
    # 		rect.topleft = xy
    # 		print(rect.topleft)

# load card assets
# deck_load = [ImageTest(file) for file in os.listdir()]
 
cardback = Image('Francese_retro_Blu.jpg', display_width / 2 + 15, display_height / 2)


# upperleft x, y coords of each player's hand (except your own)
west_north_east = [(0, (display_height - 120) / 2), ((display_width - 88) / 2, 0), (display_width - 88, (display_height - 120) / 2)]

# test hand 
test_hand = [card(Rank='A', Suit='Clubs'), card(Rank='J', Suit='Hearts'), card(Rank='7', Suit='Spades'), card(Rank='8', Suit='Clubs'), card(Rank='10', Suit='Diamonds')]



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
				t1 = threading.Thread(target = main)
				t1.start()
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

def roundOne(instr=None):
	"""
	Round 1 trump suit selection
	"""
	return False if instr!='round_1' else True

def roundTwo(instr=None):
	"""
	Round 2 trump suit selection
	"""
	return False if instr!='round_2' else True


def pickTrump():

	
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
				't_pass': TextRender('Pass', 20, 420 + 260 + int((150 - 44) / 2), 470 + 40 + int((33 - 24) / 2))
	}

	# Important variables
	rand_trump = ''

	hand = Hand()
	hand.add_(test_hand)
	hand_surf = hand.create_surf()
	hand_rect = hand.draw_rect()
	
	s = pg.Surface((440, 100))
	s.fill((255, 255, 255, 255))

	crashed = False

	# Game states
	game_state = {'round_1': False, 'round_2': False, 'pick_trump': False, 'o_pass': None, 'o_play': False}
	
	while not crashed:
		
		# get variables and commands from message queue
		try:
			msg = q.get(False)	
			print(msg)	
			if msg[0] == 'hand 1':
				hand.add_(msg[1])
				msg = ''
				print('hand is: ', hand.cards)
			elif msg[0] == 'hand 2':
				hand.clear_()
				hand.add_(msg[1])
				msg = ''
			elif msg[0] == 'rand_trump':
				print(msg, hand.cards)
				rand_trump = Image(cardToFileName(msg[1]))
				msg = ''				
				print('rand_trump is ', rand_trump)	
		except queue.Empty:
			pass

		if msg:
			game_state[msg[0]] = msg[1]

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
				
				 
				
				for surf, rect in zip(hand.create_surf(), hand.draw_rect()):
					if rect.collidepoint((mx, my)):
						print('True')

				# on FIRST ROUND of picking trump
				if game_state['round_1']:
					if play_b.collidepoint((mx, my)):
						text_dict['played_trump'] = TextRender(f'You played {trump}', 25, 420 + (440 - t_trump2.text_rect.size[0]) / 2, 470 + 2)
						game_state['pick_trump'] = True
						gp_q.put(['play'], False)

					if pass_b.collidepoint((mx, my)):
						game_state['round_1'] = False

				# on SECOND ROUND of picking trump
				if game_state['round_2']:	
					for suit, rect in zip(suits_group, suits_rect):
						if rect.collidepoint((mx, my)):
							print(files[suits_group.index(suit)])
							trump = files[suits_group.index(suit)]
							text_dict['played_trump'] = TextRender(f'You played {trump}', 25, 420 + (440 - t_trump2.text_rect.size[0]) / 2, 470 + 2)

					if pass_b.collidepoint((mx, my)):
						print('True again')

				# for i in hand_rect:
				# 	if i.collidepoint((mx, my)):
				# 		print(hand.cards[hand_rect.index(i)])
				

		# DEFAULT BLIT
		if hand.cards and rand_trump:
			for surf, rect in zip(hand.create_surf(), hand.draw_rect()):
				game_display.blit(surf, rect)

			game_display.blit(rand_trump.image, ((display_width - 88) / 2, (display_height - 120) / 2))

		# Round 1 BLIT
		if game_state['round_1']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(txt.text_surf, txt.text_rect)

			play_b = pg.draw.rect(game_display, black, (420 + 30, 470 + 40, 150, 33), 1)
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(t_play.text_surf, t_play.text_rect)
			game_display.blit(t_pass.text_surf, t_pass.text_rect)

		# Round 2 BLIT 
		
		if game_state['round_2']:	
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(t_trump2.text_surf, t_trump2.text_rect)
			
			pass_b = pg.draw.rect(game_display, black, (420 + 440 - 150 - 30, 470 + 40, 150, 33), 1)
			game_display.blit(t_pass.text_surf, t_pass.text_rect)


			for suit, rect in zip(suits_group, suits_rect):
				game_display.blit(suit, rect)
		
		if game_state['pick_trump']:
			game_display.blit(s, ((display_width - 440)/2, display_height - 250))
			game_display.blit(text_dict['played_trump'].text_surf, text_dict['played_trump'].text_rect)


		pg.display.update()

def mainLoop():

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



# create threads to handle input/output



# print('lets go')

title_screen()



