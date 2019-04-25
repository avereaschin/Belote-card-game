import pygame
import os

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

card_img = pygame.image.load('87px-12_Q_di_cuori.jpg')

def resizePicDimensions(image, width=None, height=None):

	if width and not height:
		return width, int((width * pygame.Surface.get_height(image)) / pygame.Surface.get_width(image))
	elif not width and height:
		return int((height * pygame.Surface.get_width(image)) / pygame.Surface.get_height(image)), height
	elif width and height:
		return width, height


#card_resolution = resizePicDimensions(card_img, height=75)
#card_img = pygame.transform.scale(card_img, card_resolution)
rect = card_img.get_rect()
# rect.center = (int(pygame.Surface.get_width(card_img) / 2), int(pygame.Surface.get_height(card_img) / 2))



def card(x, y):
	game_display.blit(card_img, (x, y))


x = display_width * 0.1
y = display_height - pygame.Surface.get_height(card_img)

rect.topleft = ((x, y))

print('rect center is: ', rect.center)

xy_coords = [(x + pygame.Surface.get_width(card_img) * i + 20 * i, y) for i in range(1, 6)]
print(xy_coords)

rects_ = [card_img.get_rect() for i in range(1, 6)]
for i, j in zip(rects_, xy_coords):
	i.topleft = (j)

crashed = False
clicked = False
hover = False


while not crashed:
	
	mx, my = pygame.mouse.get_pos()	

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			crashed = True

		for i in rects_:
			if event.type == pygame.MOUSEBUTTONDOWN and i.collidepoint((mx, my)):
				clicked = True
				print(True)
		# if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint((mx, my)):
		# 	clicked = True
		# if rect.collidepoint((mx, my)):
		# 	hover = True
		# else:
		# 	hover = False

		# if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint((mx, my)):
		# 	clicked = True
		# 	print('True')
		# if event.type == pygame.MOUSEBUTTONUP:
		# 	clicked = False
		# if (mx >= x and mx <= x + card_resolution[0]) and (my >= y and my <= y + card_resolution[1]):
		# 	hover = True
		# else:
		# 	hover = False
	
	game_display.fill(green)		

	# if clicked:
	# 	game_display.blit(card_img, (mx, my))
	# elif hover:
	# 	game_display.blit(card_img, (x, y - 20))
	# # elif hover:
	# # 	game_display.blit(card_img, (x, y - 20))
	# else:
	# 	game_display.blit(card_img, rect)
	
	for i in rects_:
		game_display.blit(card_img, i)
	
	pygame.display.update()
	clock.tick(60)

pygame.quit()
quit()

