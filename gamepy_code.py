import pygame as pg
import os
import time
from card_vars import ranks, suits, card, deck
import threading
from thread_test import q, inputFunc, startGame	
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
test_group = pg.sprite.Group()

# game state check for user exiting the game
crashed = False

def findMargin(hand):
	"""
	Finds topleft x coord for the first card in a given hand in order to center it on the screen
	"""
	return (display_width / 2 - ((88 * len(hand) + 6 * (len(hand) - 1)) / 2))

class ImageTest(pg.sprite.Sprite):
	"""
	Creates a sprite by adding an image and creating a rect for it
	"""

	def __init__(self, pic, x=0, y=0):
		pg.sprite.Sprite.__init__(self, test_group) 

		self.x, self.y = x, y
		self.image = pg.image.load(pic)
		split_ = lambda x: x.split('_')
		self.name = card(Rank='{}'.format(split_(pic)[0]), Suit='{}'.format(split_(pic.split('.')[0])[-1]))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

class TextRender():
	def __init__(self, text, size, x=0, y=0):

		self.text, self.size, self.x, self.y = text, size, x, y
		self.text_font = pg.font.Font('freesansbold.ttf', size)
		self.text_surf = pg.font.Font.render(self.text_font, text, False, black)
		self.text_rect = self.text_surf.get_rect()
		self.text_rect.center = (x, y)

# load card assets
deck_load = [ImageTest(file) for file in os.listdir()]
 
cardback_xy = (display_width / 2 + 15, display_height / 2)
cardback = ImageTest('Francese_retro_Blu.jpg', *cardback_xy)


# upperleft x, y coords of each player's hand (except your own)
west_north_east = [(0, (display_height - 120) / 2), ((display_width - 88) / 2, 0), (display_width - 88, (display_height - 120) / 2)]

# test hand 
hand = [card(Rank='A', Suit='Clubs'), card(Rank='J', Suit='Hearts'), card(Rank='7', Suit='Spades'), card(Rank='8', Suit='Clubs'), card(Rank='10', Suit='Diamonds')]

# upperleft (x, y) coordinates for each card in hand
xy_coords = [(findMargin(hand) + (88 + 6) * i, display_height - 120) for i in range(len(hand))]
print(xy_coords)

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
				return waitScreen()

		
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
				
			return mainLoop()				

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

		msg = ''

		try:
			msg = q.get(False)		
		except queue.Empty:
			pass

		if msg:
			return mainLoop()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				crashed = True

			
			# on left click
			# for i, j in zip(hand_load_pics, hand_rects):
			# 	if event.type == pg.MOUSEBUTTONDOWN and j.collidepoint((mx, my)):
			# 		clicked = True
			# 		val = [i, j]		
			# 	if clicked and event.type == pg.MOUSEBUTTONUP:
			# 		clicked = False			

		
		# rect_drawing = pg.draw.rect(game_display, black, [400, 300, 400, 200], 2)

		for j in range(0, 8):
			game_display.blit(pg.transform.rotate(cardback.image, 90), (0, int((display_height - 88 - 25*7) / 2 + 25 * j)))

		for j in range(0, 8):
			game_display.blit(cardback.image, (int((display_width - 88 - 25 * 7) / 2 + 25 * j), 0))

		for j in range(0, 8):
			game_display.blit(pg.transform.rotate(cardback.image, 90), (display_width - 120, int((display_height - 88 - 25*7) / 2 + 25 * j)))

		# game_display.blit(rand_card, rand_card_rect)
		
		# for i in west_north_east:
		# 		game_display.blit(cardback.image, i)

		# if clicked:
		# 	for i in hand_load_pics:
		# 		game_display.blit(val[0], (mx, my))
		# 	for i, j in zip([k for k in hand_load_pics if k != val[0]], [l for l in hand_rects if l != val[1]]):
		# 		game_display.blit(i, j)


		# else:
		# 	for i, j in zip(hand_load_pics, hand_rects):
		# 		game_display.blit(i, j)		

		for i, j in zip(hand, xy_coords):	
			for k in test_group:
				if i == k.name:
					game_display.blit(k.image, j)



		pg.display.update()

	pg.quit()
	quit()

t2 = threading.Thread(target = startGame)

print('lets go')

t2.start()

if __name__ == "__main__":
	title_screen()



