import pygame
import os
import time

os.chdir(r'Pics')

pygame.init()

display_width = 1200
display_height = 800

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 150, 0)

game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Belote')
clock = pygame.time.Clock()

# card_other = [pygame.image.load(i) for i in ['87px-11_J_di_cuori.jpg', '87px-13_K_di_cuori.jpg', '87px-38_Q_di_fiori.jpg']]
# card_img = pygame.image.load('87px-12_Q_di_cuori.jpg')


def resizePicDimensions(image, width=None, height=None):

	if width and not height:
		return width, int((width * pygame.Surface.get_height(image)) / pygame.Surface.get_width(image))
	elif not width and height:
		return int((height * pygame.Surface.get_width(image)) / pygame.Surface.get_height(image)), height
	elif width and height:
		return width, height


#card_resolution = resizePicDimensions(card_img, height=75)
#card_img = pygame.transform.scale(card_img, card_resolution)
# rect = card_img.get_rect()
# rect_other = [i.get_rect() for i in card_other]

# other_coords = [(0, 400), (600, 0), (1200 - 87, 400)]
# new_coords = [(300, 400), (600, 200), (1200 - 300 - 87, 400)]

# for i, j in zip(rect_other, other_coords):
# 	i.topleft = (j)

# rect.center = (int(pygame.Surface.get_width(card_img) / 2), int(pygame.Surface.get_height(card_img) / 2))


def card(x, y):
	game_display.blit(card_img, (x, y))


# x = display_width * 0.1
# y = display_height - pygame.Surface.get_height(card_img)

# rect.topleft = ((x, y))

# print('rect center is: ', rect.center)

# xy_coords = [(x + pygame.Surface.get_width(card_img) * i + 20 * i, y) for i in range(1, 6)]
# print(xy_coords)

# rects_ = [card_img.get_rect() for i in range(1, 6)]
# for i, j in zip(rects_, xy_coords):
# 	i.topleft = (j)

# Window is closed 

# # Card is clicked
# clicked = False
# # Card played
# played = False

# turn = False

# UPDATE_LATER = pygame.USEREVENT + 1

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def title_screen():
	
	intro = True

	while intro:

		mx, my = pygame.mouse.get_pos()	

		game_display.fill(white)
		rect_drawing1 = pygame.draw.rect(game_display, black, [(display_width / 2 - 100), display_height - 100, 200, 100])

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONDOWN and rect_drawing1.collidepoint((mx, my)):
				intro = False

		text_font = pygame.font.Font('freesansbold.ttf', 115)
		TextSurf, TextRect = text_objects('Belote', text_font)
		TextRect.center = ((display_width / 2), (display_height / 3))
		
		game_display.blit(TextSurf, TextRect)

		pygame.display.update()
		clock.tick(60)

	return mainLoop()


def mainLoop():

	crashed = False

	while not crashed:
		
		game_display.fill(green)

		# get mouse x, y coordinates
		mx, my = pygame.mouse.get_pos()	

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				crashed = True

		# 	# on left click
		# 	for i in rects_:
		# 		if event.type == pygame.MOUSEBUTTONDOWN and i.collidepoint((mx, my)):
		# 			clicked = True
		# 			val = i

		# 	for j in rect_other:
		# 		if event.type == pygame.MOUSEBUTTONDOWN and j.collidepoint((mx, my)):
		# 			turn = True
		# 			oval = j
		# 			oval.x = new_coords[rect_other.index(oval)][0]
		# 			oval.y = new_coords[rect_other.index(oval)][1]

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


		# if turn == True:

		# 	game_display.blit(card_other[rect_other.index(oval)], oval)

		# 	for j in [i for i in rects_ if i != oval]:
		# 		game_display.blit(card_img, j)

		# else:
		# 	for i, j in zip(card_other, rect_other):
		# 		game_display.blit(i, j)

		# if clicked:
		# 	game_display.blit(card_img, (mx, my))

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

title_screen()
