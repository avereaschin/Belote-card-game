import pygame
import os
import time
from card_vars import ranks, suits, card, deck
import threading
from thread_test import q, inputFunc	
import queue
from random import choice

os.chdir(r'Pics')

pygame.init()

display_width = 1280
display_height = 720

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 150, 0)
gray = (220,220,220)

game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Belote')
clock = pygame.time.Clock()

cardback_pic = pygame.image.load('Francese_retro_Blu.jpg')
cardback_rect = cardback_pic.get_rect()
cardback_rect.center = (display_width / 2 + 15, display_height / 2)

card_pics = [i for i in os.listdir()]

card_pic_dict = {}

for i in card_pics:
    if 'Francese' not in i:
        split = i.split('_')
        split_rank = split[0]
        split_suit = split[-1].split('.')[0]
        card_pic_dict[card(Rank=split_rank, Suit=split_suit)] = i

# test hand 
hand = [card(Rank='A', Suit='Clubs'), card(Rank='J', Suit='Hearts'), card(Rank='7', Suit='Spades'), card(Rank='8', Suit='Clubs'), card(Rank='10', Suit='Diamonds')]

# list of loaded card images
hand_load_pics = [pygame.image.load(card_pic_dict[i]) for i in hand]

hand_load_pics = [pygame.transform.scale(i, (88, 120)) for i in hand_load_pics]

# add rects to each card
hand_rects = [i.get_rect() for i in hand_load_pics]

def findMargin(hand):
	return (display_width / 2 - ((88 * len(hand) + 6 * (len(hand) - 1)) / 2))

# (x, y) coordinates for each card
xy_coords = [(findMargin(hand) + (88 + 6) * i, display_height - 120) for i in range(len(hand))]
print(xy_coords)

for i, j in zip(hand_rects, xy_coords):
	i.topleft = (j)

rand_card = pygame.image.load(card_pic_dict[choice(deck)])
rand_card_rect = rand_card.get_rect()
rand_card_rect.center = (display_width / 2, display_height / 2)

west_north_east = [(0, (display_height - 120) / 2), ((display_width - 88) / 2, 0), (display_width - 88, (display_height - 120) / 2)]

def card(x, y):
	game_display.blit(card_img, (x, y))


# UPDATE_LATER = pygame.USEREVENT + 1

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def title_screen():
	
	intro = True

	crashed = False
	# message = ''

	game_display.fill(white)

	while not crashed:

		mx, my = pygame.mouse.get_pos()	

		# try:
		# 	message = q.get(False)		
		# except queue.Empty:
		# 	pass

		# if message:
		# 	return mainLoop()

		rect_drawing1 = pygame.draw.rect(game_display, black, [(display_width / 2 - 100), display_height - 100, 200, 100])

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				crashed = True
			
			if event.type == pygame.MOUSEBUTTONDOWN and rect_drawing1.collidepoint((mx, my)):
				return mainLoop()

		text_font = pygame.font.Font('freesansbold.ttf', 115)
		TextSurf, TextRect = text_objects('Belote', text_font)
		TextRect.center = ((display_width / 2), (display_height / 3))
		
		game_display.blit(TextSurf, TextRect)

		pygame.display.update()

	print('about to exit title_screen')

def mainLoop():

	# Card is clicked
	clicked = False
	# Card played
	played = False
	# Exit application
	crashed = False

	while not crashed:
		
		game_display.fill(green)

		# get mouse x, y coordinates
		mx, my = pygame.mouse.get_pos()	

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				crashed = True

			# on left click
			for i, j in zip(hand_load_pics, hand_rects):
				if event.type == pygame.MOUSEBUTTONDOWN and j.collidepoint((mx, my)):
					clicked = True
					val = [i, j]		
				if clicked and event.type == pygame.MOUSEBUTTONUP:
					clicked = False


		# 	# on letting go of left click
		# 	if clicked and event.type == pygame.MOUSEBUTTONUP:
		# 		keep = val.topleft
		# 		val.topleft = ((mx, my))
				
		# 		if rect_drawing.colliderect(val):
		# 			played = True
					
		# 		else:
		# 			val.topleft = keep
		# 			played = False

		# 		clicked = False
		
				

		
		# rect_drawing = pygame.draw.rect(game_display, black, [400, 300, 400, 200], 2)

		game_display.blit(cardback_pic, cardback_rect)
		game_display.blit(rand_card, rand_card_rect)
		
		for i in west_north_east:
				game_display.blit(cardback_pic, i)

		if clicked:
			for i in hand_load_pics:
				game_display.blit(val[0], (mx, my))
			for i, j in zip([k for k in hand_load_pics if k != val[0]], [l for l in hand_rects if l != val[1]]):
				game_display.blit(i, j)


		else:
			for i, j in zip(hand_load_pics, hand_rects):
				game_display.blit(i, j)


		# if turn == True:

		# 	game_display.blit(card_other[rect_other.index(oval)], oval)

		# 	for j in [i for i in rects_ if i != oval]:
		# 		game_display.blit(card_img, j)

		# else:
		# 	for i, j in zip(card_other, rect_other):
		# 		game_display.blit(i, j)

		

		# 	for j in [i for i in rects_ if i != val]:
		# 		game_display.blit(card_img, j)
		
		# elif played:
		# 	game_display.blit(card_img, rect_drawing.center)

		# 	for j in [i for i in rects_ if i != val]:
		# 		game_display.blit(card_img, j)

		# else:
		# 	for i in rects_:
		# 		game_display.blit(card_img, i)

			


		pygame.display.update()
		clock.tick(60)

	pygame.quit()
	quit()

# t2 = threading.Thread(target = inputFunc)

# t2.start()

print('lets go')

title_screen()

# t1.start()
# t2.start()

