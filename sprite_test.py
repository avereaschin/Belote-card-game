import pygame as pg
import os

os.chdir(r'C:\Users\andre\Documents\GitHub\Belote-card-game\Pics')

pg.init()

width = 1280
height = 720

test_group = pg.sprite.Group()

class ImageTest(pg.sprite.Sprite):
	def __init__(self, pic, x, y):
		pg.sprite.Sprite.__init__(self, test_group) 

		self.image = pg.image.load(pic)
		
		self.rect = self.image.get_rect()
		self.rect.center = ((x, y))

example1 = ImageTest('7_of_Clubs.jpg', 0, 0)
example2 = ImageTest('8_of_Clubs.jpg', 300, 300)

print(test_group.sprites())

game_display = pg.display.set_mode((width, height))
pg.display.set_caption('Test')

crashed = False

while not crashed:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			crashed = True

	game_display.blit(example1.image, example1.rect)
	game_display.blit(example2.image, example2.rect)

	pg.display.update()