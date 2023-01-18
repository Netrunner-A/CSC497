from pygame import *
import sys
from os.path import abspath, dirname
import random
import math

# edit Ammar
import numpy as np
import matplotlib.pyplot as plt  
import pyautogui
import os
import cv2   
from tensorflow import keras
from random import choice
from string import ascii_uppercase
# end edit

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + '/fonts/'
IMAGE_PATH = BASE_PATH + '/images/'
SOUND_PATH = BASE_PATH + '/sounds/'

# Colors (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)
SCREEN_SIZE = (800, 600)
SCREEN = display.set_mode(SCREEN_SIZE)
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
			 'enemy1_1', 'enemy1_2',
			 'enemy2_1', 'enemy2_2',
			 'enemy3_1', 'enemy3_2',
			 'explosionblue', 'explosiongreen', 'explosionpurple',
			 'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
		  for name in IMG_NAMES}

BLOCKERS_POSITION = SCREEN_SIZE[0]-130
ENEMY_DEFAULT_POSITION = 55  # Initial value for a new game
ENEMY_MOVE_DOWN = 25  # Size of the movement for each ship towards player's ship

#edit Ammar --------------------------------------
BUILD_DATASET = False
MODEL_TESTING_MODE = False

MOVE_SET = [0, 0]

SCREEN_WIDTH = SCREEN_SIZE[0]
SCREEN_HEIGHT = SCREEN_SIZE[1]


IMAGE_WIDTH = int(SCREEN_WIDTH/5)
IMAGE_HEIGHT = int(SCREEN_HEIGHT/5)
IMAGE_SIZE = (IMAGE_HEIGHT, IMAGE_WIDTH)


if BUILD_DATASET:
	def leftdict(value):
		return 'left' if value == True else ""

	def rightdict(value):
		return 'right' if value == True else ""

	def shootdict(value):
		return 'shoot' if value == True else ""

	if not os.path.exists(BASE_PATH + "/Screenshots"):
		os.makedirs(BASE_PATH + "/Screenshots")
	if not os.path.exists(BASE_PATH + "/Screenshots/left"):
		os.makedirs(BASE_PATH + "/Screenshots/left")
	if not os.path.exists(BASE_PATH + "/Screenshots/shoot"):
		os.makedirs(BASE_PATH + "/Screenshots/shoot")
	if not os.path.exists(BASE_PATH + "/Screenshots/right"):
		os.makedirs(BASE_PATH + "/Screenshots/right")

	## Not neccesary now.
	# if not os.path.exists(BASE_PATH + "/Screenshots/leftrightshoot"):
	# 	os.makedirs(BASE_PATH + "/Screenshots/leftrightshoot")
	# if not os.path.exists(BASE_PATH + "/Screenshots/leftshoot"):
	# 	os.makedirs(BASE_PATH + "/Screenshots/leftshoot")
	# if not os.path.exists(BASE_PATH + "/Screenshots/nomove"):
	# 	os.makedirs(BASE_PATH + "/Screenshots/nomove")
	# if not os.path.exists(BASE_PATH + "/Screenshots/leftright"):
	# 	os.makedirs(BASE_PATH + "/Screenshots/leftright")
	# if not os.path.exists(BASE_PATH + "/Screenshots/rightshoot"):
	# 	os.makedirs(BASE_PATH + "/Screenshots/rightshoot")

if MODEL_TESTING_MODE:
	model = keras.models.load_model("model")



def image_processor(image):
	Array = cv2.flip(cv2.rotate(cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), IMAGE_SIZE), cv2.ROTATE_90_CLOCKWISE), 1)
	## Saving the array in a text file for troubleshooting
	# np.save("file1.txt", Array)  
	return np.reshape(Array, [1, IMAGE_HEIGHT, IMAGE_WIDTH, 3])
	
# end edit --------------------------------------

class Ship(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES['ship']
		self.rect = self.image.get_rect(topleft=(int(SCREEN_WIDTH/2), SCREEN_HEIGHT-80))
		self.speed = 5

	def update(self, keys, *args):
		if (MOVE_SET[0] or keys[K_LEFT]) and self.rect.x > 10:
			self.rect.x -= self.speed
			MOVE_SET[0] = 0
		if (MOVE_SET[1] or keys[K_RIGHT]) and self.rect.x < SCREEN_WIDTH-100:
			self.rect.x += self.speed
			MOVE_SET[1] = 0
		game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
	def __init__(self, xpos, ypos, direction, speed, filename, side):
		sprite.Sprite.__init__(self)
		self.image = IMAGES[filename]
		self.rect = self.image.get_rect(topleft=(xpos, ypos))
		self.speed = speed
		self.direction = direction
		self.side = side
		self.filename = filename

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)
		self.rect.y += self.speed * self.direction
		if self.rect.y < 15 or self.rect.y > SCREEN_WIDTH-150: # SCREEN_SIZE[0]-150 was 850
			self.kill()


class Enemy(sprite.Sprite):
	def __init__(self, row, column):
		sprite.Sprite.__init__(self)
		self.row = row
		self.column = column
		self.images = []
		self.load_images()
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.direction_x = 1
		self.direction_y = 1

	def toggle_image(self):
		self.index += 1
		if self.index >= len(self.images):
			self.index = 0
		self.image = self.images[self.index]

	def update(self, *args):
		game.screen.blit(self.image, self.rect)

	def load_images(self):
		images = {0: ['1_2', '1_1'],
				  1: ['2_2', '2_1'],
				  2: ['2_2', '2_1'],
				  3: ['3_1', '3_2'],
				  4: ['3_1', '3_2'],
				  }
		img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
					  images[self.row])
		self.images.append(transform.scale(img1, (40, 35)))
		self.images.append(transform.scale(img2, (40, 35)))


class EnemiesGroup(sprite.Group):
	def __init__(self, columns, rows):
		sprite.Group.__init__(self)
		self.enemies = [[None] * columns for _ in range(rows)]
		self.columns = columns
		self.rows = rows
		self.leftAddMove = 0
		self.rightAddMove = 0
		self.direction = 1
		#edit
		self.moveTime = 500
		self.direction_x = 1
		self.direction_y = 1
		#end edit
		self.rightMoves = 30
		self.leftMoves = 30
		self.moveNumber = 15
		self.timer = time.get_ticks()
		self.bottom = game.enemyPosition + ((rows - 1) * 45) + 35
		self._aliveColumns = list(range(columns))
		self._leftAliveColumn = 0
		self._rightAliveColumn = columns - 1

	def update(self, current_time):
		if current_time - self.timer > self.moveTime:
			if self.direction == 1:
				max_move = self.rightMoves + self.rightAddMove
			else:
				max_move = self.leftMoves + self.leftAddMove

			if self.moveNumber >= max_move:
				self.leftMoves = 30 + self.rightAddMove
				self.rightMoves = 30 + self.leftAddMove
				self.direction *= -1
				self.moveNumber = 0
				self.bottom = 0
				for enemy in self:
					enemy.rect.y += ENEMY_MOVE_DOWN
					enemy.toggle_image()
					if self.bottom < enemy.rect.y + 35:
						self.bottom = enemy.rect.y + 35
			else:

				velocity = 10 if self.direction == 1 else -10
				for enemy in self:
					enemy.rect.x += velocity
					enemy.toggle_image()
				self.moveNumber += 1

			self.timer += self.moveTime
	# def update(self, current_time):
	# 	velocity = 15
	# 	screen_border_x = SCREEN_SIZE[0]
	# 	screen_border_y = SCREEN_SIZE[1]
	# 	if current_time - self.timer > self.moveTime:
	# 		for enemy in self:
	# 			if enemy.rect.x < 150: 
	# 				enemy.direction_y *= -1
	# 				enemy.rect.x = 150
	# 			if enemy.rect.x > screen_border_x-150:
	# 				enemy.direction_x *= -1
	# 				enemy.rect.x = screen_border_x-150
	# 			if enemy.rect.y < 150: 
	# 				enemy.direction_y *= -1
	# 				enemy.rect.y = 150
	# 			if enemy.rect.y > screen_border_y-200:
	# 				enemy.direction_y *= -1
	# 				enemy.rect.y = screen_border_y-200
	# 			enemy.rect.x += velocity * enemy.direction_x
	# 			enemy.rect.y += velocity * enemy.direction_y

	# 			enemy.direction_x += enemy.direction_x + random.random() * random.choice((-0.2, 0.2))
	# 			enemy.direction_y += enemy.direction_y + random.random() * random.choice((-0.2, 0.2))
	# 			if enemy.direction_x > 1 or enemy.direction_x < -1:
	# 				enemy.direction_x = random.random() * random.choice((-1, 1))
	# 			if enemy.direction_y > 1 or enemy.direction_y < -1:
	# 				enemy.direction_y = random.random() * random.choice((-1, 1))
	# 			#print("x:{} y:{} dir_x:{} dir_y:{}".format(enemy.rect.x, enemy.rect.y, enemy.direction_x, enemy.direction_y))
	# 			enemy.toggle_image()
	# 		self.timer += self.moveTime


	#def update(self, current_time):
	#	velocity = 10
	#	if current_time - self.timer > self.moveTime:
	#		for enemy in self:
	#			if enemy.direction_x < 0:
	#				if enemy.rect.x < 50:
	#					enemy.direction_x = 1
	#				enemy.rect.x += velocity * enemy.direction_x
	#				enemy.direction_x = enemy.direction_x + random.randint(0, 1)*0.15
	#			elif enemy.direction_x >= 1:
	#				if enemy.rect.x > 850:
	#					enemy.direction_x = -1
	#				enemy.rect.x += velocity * enemy.direction_x
	#				enemy.direction_x = enemy.direction_x + random.randint(-1, 0)*0.15

	#			if enemy.direction_y < 0:
	#				if enemy.rect.y < 50:
	#					enemy.direction_y = 1
	#				enemy.rect.y += velocity * enemy.direction_y
	#				enemy.direction_y = enemy.direction_y + random.randint(0, 1)*0.15
	#			elif enemy.direction_y >= 1:
	#				if enemy.rect.y > 500:
	#					enemy.direction_y = -1
	#				enemy.rect.y += velocity * enemy.direction_y
	#				enemy.direction_y = enemy.direction_y + random.randint(-1, 0)*0.15
	#			
	#			enemy.toggle_image()

	def add_internal(self, *sprites):
		super(EnemiesGroup, self).add_internal(*sprites)
		for s in sprites:
			self.enemies[s.row][s.column] = s

	def remove_internal(self, *sprites):
		super(EnemiesGroup, self).remove_internal(*sprites)
		for s in sprites:
			self.kill(s)
		self.update_speed()

	def is_column_dead(self, column):
		return not any(self.enemies[row][column]
					   for row in range(self.rows))

	def random_bottom(self):
		rans = [e for e in self.sprites()]
		return random.choice(rans)

	def update_speed(self):
		if len(self) == 1:
			self.moveTime = 200
		elif len(self) <= 10:
			self.moveTime = 400

	def kill(self, enemy):
		self.enemies[enemy.row][enemy.column] = None
		is_column_dead = self.is_column_dead(enemy.column)
		# if is_column_dead:
		#   self._aliveColumns.remove(enemy.column)

		if enemy.column == self._rightAliveColumn:
			while self._rightAliveColumn > 0 and is_column_dead:
				self._rightAliveColumn -= 1
				self.rightAddMove += 5
				is_column_dead = self.is_column_dead(self._rightAliveColumn)

		elif enemy.column == self._leftAliveColumn:
			while self._leftAliveColumn < self.columns and is_column_dead:
				self._leftAliveColumn += 1
				self.leftAddMove += 5
				is_column_dead = self.is_column_dead(self._leftAliveColumn)


class Blocker(sprite.Sprite):
	def __init__(self, size, color, row, column):
		sprite.Sprite.__init__(self)
		self.height = size
		self.width = size
		self.color = color
		self.image = Surface((self.width, self.height))
		self.image.fill(self.color)
		self.rect = self.image.get_rect()
		self.row = row
		self.column = column

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES['mystery']
		self.image = transform.scale(self.image, (75, 35))
		self.rect = self.image.get_rect(topleft=(-80, 45))
		self.row = 5
		self.moveTime = 25000
		self.direction = 1
		self.timer = time.get_ticks()
		self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
		self.mysteryEntered.set_volume(0.3)
		self.playSound = True

	def update(self, keys, currentTime, *args):
		resetTimer = False
		passed = currentTime - self.timer
		if passed > self.moveTime:
			if (self.rect.x < 0 or self.rect.x > SCREEN_WIDTH) and self.playSound:
				self.mysteryEntered.play()
				self.playSound = False
			if self.rect.x < SCREEN_WIDTH+40 and self.direction == 1:
				self.mysteryEntered.fadeout(4000)
				self.rect.x += 2
				game.screen.blit(self.image, self.rect)
			if self.rect.x > -100 and self.direction == -1:
				self.mysteryEntered.fadeout(4000)
				self.rect.x -= 2
				game.screen.blit(self.image, self.rect)

		if self.rect.x > 830:
			self.playSound = True
			self.direction = -1
			resetTimer = True
		if self.rect.x < -90:
			self.playSound = True
			self.direction = 1
			resetTimer = True
		if passed > self.moveTime and resetTimer:
			self.timer = currentTime


class EnemyExplosion(sprite.Sprite):
	def __init__(self, enemy, *groups):
		super(EnemyExplosion, self).__init__(*groups)
		self.image = transform.scale(self.get_image(enemy.row), (40, 35))
		self.image2 = transform.scale(self.get_image(enemy.row), (50, 45))
		self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
		self.timer = time.get_ticks()

	@staticmethod
	def get_image(row):
		img_colors = ['purple', 'blue', 'blue', 'green', 'green']
		return IMAGES['explosion{}'.format(img_colors[row])]

	def update(self, current_time, *args):
		passed = current_time - self.timer
		if passed <= 100:
			game.screen.blit(self.image, self.rect)
		elif passed <= 200:
			game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
		elif 400 < passed:
			self.kill()


class MysteryExplosion(sprite.Sprite):
	def __init__(self, mystery, score, *groups):
		super(MysteryExplosion, self).__init__(*groups)
		self.text = Text(FONT, 20, str(score), WHITE,
						 mystery.rect.x + 20, mystery.rect.y + 6)
		self.timer = time.get_ticks()

	def update(self, current_time, *args):
		passed = current_time - self.timer
		if passed <= 200 or 400 < passed <= 600:
			self.text.draw(game.screen)
		elif 600 < passed:
			self.kill()


class ShipExplosion(sprite.Sprite):
	def __init__(self, ship, *groups):
		super(ShipExplosion, self).__init__(*groups)
		self.image = IMAGES['ship']
		self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
		self.timer = time.get_ticks()

	def update(self, current_time, *args):
		passed = current_time - self.timer
		if 300 < passed <= 600:
			game.screen.blit(self.image, self.rect)
		elif 900 < passed:
			self.kill()


class Life(sprite.Sprite):
	def __init__(self, xpos, ypos):
		sprite.Sprite.__init__(self)
		self.image = IMAGES['ship']
		self.image = transform.scale(self.image, (40, 40))
		self.rect = self.image.get_rect(topleft=(xpos, ypos))

	def update(self, *args):
		game.screen.blit(self.image, self.rect)


class Text(object):
	def __init__(self, textFont, size, message, color, xpos, ypos):
		self.font = font.Font(textFont, size)
		self.surface = self.font.render(message, True, color)
		self.rect = self.surface.get_rect(topleft=(xpos, ypos))

	def draw(self, surface):
		surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
	def __init__(self):

		mixer.pre_init(44100, -16, 1, 4096)
		init()
		self.clock = time.Clock()
		self.caption = display.set_caption('Space Invaders')
		self.screen = SCREEN
		self.background = transform.scale(image.load(IMAGE_PATH + 'background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
		self.startGame = False
		self.mainScreen = True
		self.gameOver = False

		# Counter for enemy starting position (increased each new round)
		self.enemyPosition = ENEMY_DEFAULT_POSITION
		self.titleText = Text(FONT, int(SCREEN_HEIGHT/10), 'Space Invaders', WHITE, int(SCREEN_WIDTH/6.0975), int(SCREEN_HEIGHT/4.5161))
		self.titleText2 = Text(FONT, int(SCREEN_HEIGHT/20), 'Press any key to continue', WHITE,
							   int(SCREEN_WIDTH/4.545454545454546), int(SCREEN_HEIGHT/3.1111))
		# game over text
		self.gameOverText = Text(FONT, int(SCREEN_HEIGHT/10), 'Game Over', WHITE, int(SCREEN_WIDTH/4.0), int(SCREEN_HEIGHT/2.5925))
		# game finished text
		self.gameFinishedText1 = Text(FONT, 60, 'Congratulations! ', WHITE, int(SCREEN_WIDTH/6.6666), int(SCREEN_HEIGHT/3.1818))
		self.gameFinishedText2 = Text(FONT, 60, 'You saved the planet! ', WHITE, int(SCREEN_WIDTH/10.0), int(SCREEN_HEIGHT/2.0588))
		# next level text
		self.nextLevel = Text(FONT, 70, 'Next Level', WHITE, 240, 270)
		self.enemy1Text = Text(FONT, int(SCREEN_HEIGHT/20), '  =  10 pts', GREEN, int(SCREEN_WIDTH/2.2), int(SCREEN_HEIGHT/2.5925))
		self.enemy2Text = Text(FONT, int(SCREEN_HEIGHT/20), '  =  20 pts', BLUE, int(SCREEN_WIDTH/2.2), int(SCREEN_HEIGHT/2.1875))
		self.enemy3Text = Text(FONT, int(SCREEN_HEIGHT/20), '  =  30 pts', PURPLE, int(SCREEN_WIDTH/2.2), int(SCREEN_HEIGHT/1.8918))
		self.enemy4Text = Text(FONT, int(SCREEN_HEIGHT/20), '  =  ?????', RED, int(SCREEN_WIDTH/2.2), int(SCREEN_HEIGHT/1.6666))
		self.scoreText = Text(FONT, 30, 'Score: ', WHITE, 5, 5)
		self.livesText = Text(FONT, 30, 'Lives:  ', WHITE, SCREEN_WIDTH - 270, int(SCREEN_HEIGHT/140.0))
		self.CurrentLevel = Text(FONT, 30, 'Level:  ', WHITE, int(SCREEN_WIDTH/2.7027), int(SCREEN_HEIGHT/140.0))

		# player's lives:
		self.life1 = Life(SCREEN_WIDTH - 150, 3)
		self.life2 = Life(SCREEN_WIDTH - 100, 3)
		self.life3 = Life(SCREEN_WIDTH - 50, 3)
		self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

	def reset(self, score, lvl):
		self.player = Ship()
		self.playerGroup = sprite.Group(self.player)
		self.explosionsGroup = sprite.Group()
		self.bullets = sprite.Group()
		self.mysteryShip = Mystery()
		self.mysteryGroup = sprite.Group(self.mysteryShip)
		self.enemyBullets = sprite.Group()
		self.make_enemies(lvl)
		self.allSprites = sprite.Group(self.player, self.enemies,
									   self.livesGroup, self.mysteryShip)
		self.keys = key.get_pressed()

		self.timer = time.get_ticks()
		self.noteTimer = time.get_ticks()
		self.shipTimer = time.get_ticks()
		self.score = score
		self.create_audio()
		self.makeNewShip = False
		self.shipAlive = True

	def make_blockers(self, number):
		blockerGroup = sprite.Group()
		for row in range(4):
			for column in range(9):
				blocker = Blocker(10, GREEN, row, column)
				blocker.rect.x = SCREEN_WIDTH/20 + (SCREEN_WIDTH/5 * number) + (column * blocker.width)
				blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
				blockerGroup.add(blocker)
		return blockerGroup

	def create_audio(self):
		self.sounds = {}
		for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
						   'shipexplosion']:
			self.sounds[sound_name] = mixer.Sound(
				SOUND_PATH + '{}.wav'.format(sound_name))
			self.sounds[sound_name].set_volume(0.2)

		self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i
						   in range(4)]
		for sound in self.musicNotes:
			sound.set_volume(0.5)

		self.noteIndex = 0

	def play_main_music(self, currentTime):
		if currentTime - self.noteTimer > self.enemies.moveTime:
			self.note = self.musicNotes[self.noteIndex]
			if self.noteIndex < 3:
				self.noteIndex += 1
			else:
				self.noteIndex = 0

			self.note.play()
			self.noteTimer += self.enemies.moveTime

	@staticmethod
	def should_exit(evt):
		return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

	def check_input(self):
		self.keys = key.get_pressed()
		for e in event.get():
			if self.should_exit(e):
				sys.exit()
			if e.type == KEYDOWN:
				if e.key == K_SPACE:
					if len(self.bullets) == 0 and self.shipAlive:
						if self.score < 1000:
							bullet = Bullet(self.player.rect.x + 23,
											self.player.rect.y + 5, -1,
											15, 'laser', 'center')
							self.bullets.add(bullet)
							self.allSprites.add(self.bullets)
							self.sounds['shoot'].play()
						else:
							leftbullet = Bullet(self.player.rect.x + 8,
												self.player.rect.y + 5, -1,
												15, 'laser', 'left')
							rightbullet = Bullet(self.player.rect.x + 38,
												 self.player.rect.y + 5, -1,
												 15, 'laser', 'right')
							self.bullets.add(leftbullet)
							self.bullets.add(rightbullet)
							self.allSprites.add(self.bullets)
							self.sounds['shoot2'].play()

	def make_enemies(self, lvl):
		colnum = lvl + 2
		# level one
		if lvl == 1:
			enemies = EnemiesGroup(colnum, 1)
			for row in range(1):
				for column in range(colnum):
					enemy = Enemy(row, column)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

		# level two
		elif lvl == 2:
			enemies = EnemiesGroup(colnum + 2, 1)
			for column in range(6):
				if column % 2 == 0:
					enemy = Enemy(0, column + 1)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 35)
					enemy.rect.y = self.enemyPosition
					enemies.add(enemy)
				else:
					enemy = Enemy(0, column)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 35)
					enemy.rect.y = self.enemyPosition + (25)
					enemies.add(enemy)

			self.enemies = enemies

		# level three
		elif lvl == 3:
			enemies = EnemiesGroup(colnum + 7, 1)
			for column in range(12):
				if column % 3 == 0:
					enemy = Enemy(0, column)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
					enemy.rect.y = self.enemyPosition
					enemies.add(enemy)
				elif column % 3 == 1:
					enemy = Enemy(0, column)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
					enemy.rect.y = self.enemyPosition + 45
					enemies.add(enemy)
				else:
					enemy = Enemy(0, column)
					enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
					enemy.rect.y = self.enemyPosition + 85
					enemies.add(enemy)
			self.enemies = enemies

		# level four
		elif lvl == 4:
			enemies = EnemiesGroup(colnum * 3, 2)
			for row in range(2):
				for column in range(9):
					if column % 3 == 0:
						enemy = Enemy(row, column + 1)
						enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
						enemy.rect.y = self.enemyPosition + (row * 35)
						enemies.add(enemy)
					elif column % 3 == 1:
						enemy = Enemy(row, column + 1)
						enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
						enemy.rect.y = self.enemyPosition + (row * 65)
						enemies.add(enemy)
					else:
						enemy = Enemy(row, column + 1)
						enemy.rect.x = SCREEN_WIDTH/6.3694 + (column * 50)
						enemy.rect.y = self.enemyPosition + (row * 95)
						enemies.add(enemy)
			self.enemies = enemies

		# level five
		elif lvl == 5:
			Xcord1 = 120
			Xcord2 = 160
			Ycord1 = 120
			enemies = EnemiesGroup(colnum + 13, 2)
			# two rows
			for row in range(2):
				for column in range(20):
					if row == 0:
						if column % 2 == 0:
							enemy = Enemy(0, column + 1)
							enemy.rect.x = Xcord1 + (column * 35)
							enemy.rect.y = self.enemyPosition
							enemies.add(enemy)
						else:
							enemy = Enemy(0, column)
							enemy.rect.x = Xcord1 + (column * 35)
							enemy.rect.y = self.enemyPosition + 25
							enemies.add(enemy)
					else:
						if column % 2 == 0:
							enemy = Enemy(0, column + 1)
							enemy.rect.x = Xcord2 + (column * 35)
							enemy.rect.y = self.enemyPosition + 85
							enemies.add(enemy)
						else:
							enemy = Enemy(0, column)
							enemy.rect.x = Xcord2 + (column * 35)
							enemy.rect.y = self.enemyPosition + Ycord1
							enemies.add(enemy)
			self.enemies = enemies

		# level six
		elif lvl == 6:
			enemies = EnemiesGroup(colnum + 7, 3)
			for row in range(3):
				for column in range(15):
					enemy = Enemy(row, column)
					enemy.rect.x = 157 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

		# level seven
		elif lvl == 7:
			enemies = EnemiesGroup(colnum, 1)
			for row in range(1):
				for column in range(colnum):
					enemy = Enemy(row, column)
					enemy.rect.x = 157 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

		# level eight
		elif lvl == 8:
			enemies = EnemiesGroup(colnum, 1)
			for row in range(1):
				for column in range(colnum):
					enemy = Enemy(row, column)
					enemy.rect.x = 157 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

		# level nine
		elif lvl == 9:
			enemies = EnemiesGroup(colnum, 1)
			for row in range(1):
				for column in range(colnum):
					enemy = Enemy(row, column)
					enemy.rect.x = 157 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

		# level ten
		elif lvl == 10:
			enemies = EnemiesGroup(colnum, 1)
			for row in range(1):
				for column in range(colnum):
					enemy = Enemy(row, column)
					enemy.rect.x = 157 + (column * 50)
					enemy.rect.y = self.enemyPosition + (row * 45)
					enemies.add(enemy)
			self.enemies = enemies

	def make_enemies_shoot(self):
		if (time.get_ticks() - self.timer) > 700 and self.enemies:
			enemy = self.enemies.random_bottom()
			self.enemyBullets.add(
				Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
					   'enemylaser', 'center'))
			self.allSprites.add(self.enemyBullets)
			self.timer = time.get_ticks()

	def calculate_score(self, row):
		scores = {0: 30,
				  1: 20,
				  2: 20,
				  3: 10,
				  4: 10,
				  5: random.choice([50, 100, 150, 300])
				  }

		score = scores[row]
		self.score += score
		return score

	def create_main_menu(self):
		self.enemy1 = IMAGES['enemy3_1']
		self.enemy1 = transform.scale(self.enemy1, (40, 40))
		self.enemy2 = IMAGES['enemy2_2']
		self.enemy2 = transform.scale(self.enemy2, (40, 40))
		self.enemy3 = IMAGES['enemy1_2']
		self.enemy3 = transform.scale(self.enemy3, (40, 40))
		self.enemy4 = IMAGES['mystery']
		self.enemy4 = transform.scale(self.enemy4, (80, 40))
		self.screen.blit(self.enemy1, (int(SCREEN_WIDTH/3.1446), int(SCREEN_HEIGHT/2.5925)))
		self.screen.blit(self.enemy2, (int(SCREEN_WIDTH/3.1446), int(SCREEN_HEIGHT/2.1875)))
		self.screen.blit(self.enemy3, (int(SCREEN_WIDTH/3.1446), int(SCREEN_HEIGHT/1.8918)))
		self.screen.blit(self.enemy4, (int(SCREEN_WIDTH/3.3444), int(SCREEN_HEIGHT/1.6666)))

	def check_collisions(self):
		sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

		# enemies collisions check
		for enemy in sprite.groupcollide(self.enemies, self.bullets,
										 True, True).keys():
			self.sounds['invaderkilled'].play()
			self.calculate_score(enemy.row)
			EnemyExplosion(enemy, self.explosionsGroup)
			self.gameTimer = time.get_ticks()

		# mystery collisions check
		for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
										   True, True).keys():
			mystery.mysteryEntered.stop()
			self.sounds['mysterykilled'].play()
			score = self.calculate_score(mystery.row)
			MysteryExplosion(mystery, score, self.explosionsGroup)
			newShip = Mystery()
			self.allSprites.add(newShip)
			self.mysteryGroup.add(newShip)

		# player collisions check
		for player in sprite.groupcollide(self.playerGroup, self.enemyBullets,
										  True, True).keys():
			if self.life3.alive():
				self.life3.kill()
			elif self.life2.alive():
				self.life2.kill()
			elif self.life1.alive():
				self.life1.kill()
			else:
				self.gameOver = True
				self.startGame = False
			self.sounds['shipexplosion'].play()
			ShipExplosion(player, self.explosionsGroup)
			self.makeNewShip = True
			self.shipTimer = time.get_ticks()
			self.shipAlive = False

		# enemies collisions check due to player not able to kill them all.
		if self.enemies.bottom >= 540:
			sprite.groupcollide(self.enemies, self.playerGroup, True, True)
			if not self.player.alive() or self.enemies.bottom >= 600:
				self.gameOver = True
				self.startGame = False

		sprite.groupcollide(self.bullets, self.allBlockers, True, True)
		sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
		if self.enemies.bottom >= BLOCKERS_POSITION:
			sprite.groupcollide(self.enemies, self.allBlockers, False, True)

	def create_new_ship(self, createShip, currentTime):
		if createShip and (currentTime - self.shipTimer > 900):
			self.player = Ship()
			self.allSprites.add(self.player)
			self.playerGroup.add(self.player)
			self.makeNewShip = False
			self.shipAlive = True

	# responsible for the screen that appears to the user, in case the user lost.
	def create_game_over(self, currentTime):
		self.screen.blit(self.background, (0, 0))
		passed = currentTime - self.timer
		if passed < 750:
			self.gameOverText.draw(self.screen)
		elif 750 < passed < 1500:
			self.screen.blit(self.background, (0, 0))
		elif 1500 < passed < 2250:
			self.gameOverText.draw(self.screen)
		elif 2250 < passed < 2750:
			self.screen.blit(self.background, (0, 0))
		elif passed > 3000:
			self.mainScreen = True

		for e in event.get():
			if self.should_exit(e):
				sys.exit()

	# responsible for the screen that appears to the user, in case the user won.
	def create_game_won(self, currentTime):
		passed = currentTime - self.timer
		if passed < 1000:
			self.gameFinishedText1.draw(self.screen)
			self.gameFinishedText2.draw(self.screen)
		elif 1000 < passed < 1500:
			self.screen.blit(self.background, (0, 0))
		elif 1500 < passed < 2700:
			self.gameFinishedText1.draw(self.screen)
			self.gameFinishedText2.draw(self.screen)
		elif 2700 < passed < 2950:
			self.screen.blit(self.background, (0, 0))
		elif passed > 3000:
			self.mainScreen = True

		for e in event.get():
			if self.should_exit(e):
				sys.exit()

	def main(self):
		Levels_count = 1
		screenshot = np.ndarray((1, IMAGE_HEIGHT, IMAGE_WIDTH, 3))
		while True:
			if self.mainScreen:
				self.screen.blit(self.background, (0, 0))
				self.titleText.draw(self.screen)
				self.titleText2.draw(self.screen)
				self.enemy1Text.draw(self.screen)
				self.enemy2Text.draw(self.screen)
				self.enemy3Text.draw(self.screen)
				self.enemy4Text.draw(self.screen)
				self.create_main_menu()
				for e in event.get():
					if self.should_exit(e):
						sys.exit()
					if e.type == KEYUP:
						# Only create blockers on a new game, not a new round
						self.allBlockers = sprite.Group(self.make_blockers(0),
														self.make_blockers(1),
														self.make_blockers(2),
														self.make_blockers(3),
														self.make_blockers(4))
						self.livesGroup.add(self.life1, self.life2, self.life3)
						self.reset(0, Levels_count)
						self.startGame = True
						self.mainScreen = False

			elif self.startGame:
				if not self.enemies and not self.explosionsGroup:
					currentTime = time.get_ticks()
					# next level window
					if currentTime - self.gameTimer < 3000:
						self.screen.blit(self.background, (0, 0))
						if Levels_count < 10:
							self.nextLevel.draw(self.screen)
							self.check_input()
						else:
							self.create_game_won(currentTime)

					if currentTime - self.gameTimer > 3000:
						# Move enemies closer to bottom
						self.enemyPosition += ENEMY_MOVE_DOWN
						Levels_count += 1
						self.reset(self.score, Levels_count)
						self.gameTimer += 3000
				# the game process at the current level
				else:
					currentTime = time.get_ticks()
					self.play_main_music(currentTime)
					self.screen.blit(self.background, (0, 0))
					self.allBlockers.update(self.screen)
					# level presentation
					self.scoreText2 = Text(FONT, 30, str(self.score), GREEN, 135, 5)
					self.scoreText.draw(self.screen)
					self.scoreText2.draw(self.screen)
					# level presentation
					self.LevelText2 = Text(FONT, 30, str(Levels_count), BLUE, int(SCREEN_WIDTH/2.7027) + 130, int(SCREEN_HEIGHT/140.0))
					self.CurrentLevel.draw(self.screen)
					self.LevelText2.draw(self.screen)
					self.livesText.draw(self.screen)
					# edit Ammar
					# {'leftshoot': 0, 'left': 1, 'shoot': 2, 'rightshoot': 3, 'right': 4}
					
					if MODEL_TESTING_MODE:
						if currentTime % 10 == 2:
							pred_model = model.predict(screenshot, verbose = 0)
							move = np.argmax(pred_model, axis = 1)
							if move == 0:
								# left + shoot
								# print("left + shoot")
								MOVE_SET[0] = 1
								event.post(event.Event(KEYDOWN, key=K_SPACE))
							#elif move == 1:
							#    # left
							#    # print("left")
							#    MOVE_SET[0] = 1
							elif move == 1: 
								# shoot
								#print("shoot")
								event.post(event.Event(KEYDOWN, key=K_SPACE))
							#elif move == 3:
							#    # right + shoot
							#    # print("right + shoot")
							#    MOVE_SET[1] = 1
								event.post(event.Event(KEYDOWN, key=K_SPACE))
							elif move == 2:
								# right
								# print("right")
								MOVE_SET[1] = 1

					# end edit
					self.check_input()
					self.enemies.update(currentTime)
					self.allSprites.update(self.keys, currentTime)
					self.explosionsGroup.update(currentTime)
					self.check_collisions()
					self.create_new_ship(self.makeNewShip, currentTime)
					self.make_enemies_shoot()
					## edit Ammar V1 --------------------------------------
					#if currentTime % 10 == 0:
					#    image.save(self.screen,"images/screenshot{}.jpg".format(currentTime))
					#    with open("Moveset.txt", "a") as file1:
					#        file1.write("{}, {}, {}, {}/n".format(currentTime, self.keys[K_LEFT], self.keys[K_RIGHT], self.keys[K_SPACE]))
					#        file1.close()
					# edit Ammar V2 --------------------------------------            
					if MODEL_TESTING_MODE:
						if currentTime % 10 == 1:
							screenshot = image_processor(surfarray.pixels3d(self.screen))

					if BUILD_DATASET:
						if currentTime % 10 == 0:
							savepath = "{}{}{}".format(leftdict(self.keys[K_LEFT]), rightdict(self.keys[K_RIGHT]), shootdict(self.keys[K_SPACE]))
							#if not savepath:
							#    savepath = "nomove"
							if savepath == "left":
								image.save(self.screen, BASE_PATH + "/Screenshots/left/screenshot{}.jpg".format(''.join(choice(ascii_uppercase) for i in range(5))))
							elif savepath == "right":
								image.save(self.screen, BASE_PATH + "/Screenshots/right/screenshot{}.jpg".format(''.join(choice(ascii_uppercase) for i in range(5))))
							elif savepath == "shoot":
								image.save(self.screen, BASE_PATH + "/Screenshots/shoot/screenshot{}.jpg".format(''.join(choice(ascii_uppercase) for i in range(5))))
					# end edit --------------------------------------
					
			elif self.gameOver:
				currentTime = time.get_ticks()
				# Reset enemy starting position
				self.enemyPosition = ENEMY_DEFAULT_POSITION
				self.create_game_over(currentTime)
				Levels_count = 1

			display.update()
			self.clock.tick(60)


if __name__ == '__main__':
	game = SpaceInvaders()
	game.main()