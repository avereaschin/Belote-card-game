import pygame as pg
import os
from card_vars import ranks, suits, card, deck

os.chdir(r'C:\Users\andre\Documents\GitHub\Belote-card-game\Pics')

pg.init()

width = 1280
height = 720

class ImageTest(pg.sprite.Sprite):
	def __init__(self, pic):
		pg.sprite.Sprite.__init__(self, test_group) 

		self.image = pg.image.load(pic)
		self.name = pic
		
		self.rect = self.image.get_rect()


test_group = pg.sprite.Group()

for i in ['7_of_Clubs.jpg', '8_of_Clubs.jpg']:
	ImageTest(i)
for i, j in zip(test_group, [(100, 100), (300, 300)]):
	i.rect.center = j


print(test_group.sprites())

game_display = pg.display.set_mode((width, height))
pg.display.set_caption('Test')

crashed = False

for i in test_group:
	print(i.name)

while not crashed:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			crashed = True

	for i in test_group:
		game_display.blit(i.image, i.rect)

	pg.display.update()