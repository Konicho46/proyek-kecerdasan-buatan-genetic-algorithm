import pygame
import sge
import random
import game

pygame.init()
pygame.mixer.init()

# Shootsound
SHOOT_SOUND = pygame.mixer.Sound('Assets/laser.wav')
SHOOT_SOUND.set_volume(1)

# destroy sound
DESTROY_SOUND = pygame.mixer.Sound('Assets/destroy.wav')
DESTROY_SOUND.set_volume(0.3)


# play backgorund music
pygame.mixer.music.load('Assets/arcade.wav')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


#upgrade music
UPGRADE_SOUND = pygame.mixer.Sound('Assets/upgrade.wav')
UPGRADE_SOUND.set_volume(1)


class Kraken(sge.dsp.Object):
    gene_props = {
        # Ukuran
        'scale': {
            'min': 1,
            'max': 7,
            'gen': lambda: random.gammavariate(4, 0.5) + 1
        },
        # kecepatan
        'xvelocity': {
            'min': 0.01,
            'max': 5,
            'gen': lambda: random.gammavariate(2, 0.4)
        },
        'yvelocity': {
            'min': 0.01,
            'max': 5,
            'gen': lambda: random.gammavariate(2, 0.3)
        },
        # perpindahan arah
        'x_prob_change_dir': {
            'min': 0.01,
            'max': 0.06,
            'gen': lambda: random.uniform(0.0, 0.05)
        },
        'y_prob_change_dir': {
            'min': 0.0,
            'max': 0.06,
            'gen': lambda: random.uniform(0.0, 0.05)
        },
        # warna
        'colors': ['red', 'blue', 'green', 'yellow', 'pink', 'purple', 'violet']
    }

    @staticmethod
    def _generate_gen(name):
        if name == 'colors':
            return random.choice(Kraken.gene_props[name])
        v = Kraken.gene_props[name]['gen']()
        max_v = Kraken.gene_props[name]['max']
        min_v = Kraken.gene_props[name]['min']
        if v < min_v:
            return min_v
        elif v > max_v:
            return max_v
        else:
            return v

    def __init__(self, **kwargs):
        # Generate random values and update with the ones provided in kwargs
        self.attributes = {
            k: self._generate_gen(k) for k in self.gene_props.keys()
        }
        self.attributes.update(kwargs)

        self.genes = self.attributes

        # Asset musuh
        super(Kraken, self).__init__(sge.game.width / 2., sge.game.height / 2. - 80,
                                      sprite=sge.gfx.Sprite(name='E_kraken'),
                                      checks_collisions=False)

        self.xvelocity = self.attributes.get('xvelocity')
        self.yvelocity = self.attributes.get('yvelocity')
        scale = self.attributes.get('scale')
        self.bbox_width = (self.sprite.width * scale)
        self.bbox_height = (self.sprite.height * scale)
        color = self.attributes.get('colors')
        self.image_blend = sge.gfx.Color(color)
        self.image_xscale = scale
        self.image_yscale = scale
        self.fitness = 0

    # Event step merupakan Event Listener yang terkait dengan library sge berarti
    # konsep untuk merespon kegiatan yang terjadi didalam suatuobjek.

    def event_step(self, time_passed, delta_mult):
        self.fitness += 1
        # Change directions
        if random.random() <= self.attributes.get('x_prob_change_dir'):
            self.xvelocity = -self.xvelocity
        if random.random() <= self.attributes.get('y_prob_change_dir'):
            self.yvelocity = -self.yvelocity

        # Bouncing off the edges and the wall
        if self.bbox_left < 0:
            self.bbox_left = 0
            self.xvelocity = abs(self.xvelocity)
        elif self.bbox_right > sge.game.current_room.width:
            self.bbox_right = sge.game.current_room.width
            self.xvelocity = -abs(self.xvelocity)
        if self.bbox_top < 0:
            self.bbox_top = 0
            self.yvelocity = abs(self.yvelocity)
        if self.bbox_bottom > game.RESY - (game.WALL_YOFFSET + game.WALL_HEIGHT):
            self.bbox_bottom = game.RESY - (game.WALL_YOFFSET + game.WALL_HEIGHT)
            self.yvelocity = -abs(self.yvelocity)



class Player(sge.dsp.Object):

    def __init__(self):
        self.lkey = "left"
        self.rkey = "right"
        self.double = False
        self.triple = False
        self.laser = False
        self.double_laser = False
        x = sge.game.width / 2.
        y = sge.game.height - game.PLAYER_YOFFSET
        # asset player
        super(Player, self).__init__(x, y, sprite=sge.gfx.Sprite(name='spaceplane'), tangible=False)

        # Load the shoot sound
        self.shoot_sound = SHOOT_SOUND


    def event_step(self, time_passed, delta_mult):
        # Movement
        key_motion = (sge.keyboard.get_pressed(self.rkey) -
                      sge.keyboard.get_pressed(self.lkey))
        self.xvelocity = key_motion * game.PLAYER_SPEED

        # "Animate" the sprite according to the moving direction
        if key_motion > 0 and self.image_xscale < 0:
            self.image_xscale = 1

        elif key_motion < 0 and self.image_xscale > 0:
            self.image_xscale = -1

        # Keep the paddle inside the window
        if self.bbox_left < 0:
            self.bbox_left = 0
        elif self.bbox_right > sge.game.current_room.width:
            self.bbox_right = sge.game.current_room.width

    def event_key_press(self, key, char):
        # Shooting
        if not sge.game.game_over and key == 'space':
            # The number of krakens must be higher than the minimum allowed,
            # and the number of bullets lower than the maximum
            nkrakens = sum(1 for o in sge.game.current_room.objects
                            if isinstance(o, Kraken))
            nbullets = sum(1 for o in sge.game.current_room.objects
                           if isinstance(o, PlayerBullet))
            if nkrakens > game.MIN_NKRAKENS and nbullets <= nkrakens / 10:
                # Play the shoot sound
                self.shoot_sound.play()

                # Add the bullet object
                sge.game.current_room.add(PlayerBullet(self))
                if game.DOUBLE_SHOOT == True:
                    self.double = True
                    sge.game.current_room.add(PlayerBullet(self))
                    self.double = False
                if game.TRIPLE_SHOOT == True:
                    self.double = True
                    self.triple = True
                    sge.game.current_room.add(PlayerBullet(self))
                    self.double = False
                    self.triple = False
                if game.LASER_SHOT == True:
                    self.laser = True
                    sge.game.current_room.add(PlayerBullet(self))
                    self.laser = False
                if game.DOUBLE_LASER_SHOT == True:
                    self.double_laser = True
                    sge.game.current_room.add(PlayerBullet(self))
                    self.double_laser = False


class PlayerBullet(sge.dsp.Object):
    def __init__(self, player):
        self.bullet_size = 1
        self.bullet_speed = 5
        self.upgrade_sound = UPGRADE_SOUND
        self.killed = False

        # The bullet appears out of the spaceplane
        if game.DOUBLE_SHOOT == False:
            x = player.x + player.bbox_width / 2 + 4
        elif game.TRIPLE_SHOOT == True:
            if player.double == True:
                x = player.x + player.bbox_width - 2
                if player.triple == True:
                    x = player.x + player.bbox_width / 2 + 4
            else:
                x = player.x + 10
        elif game.DOUBLE_SHOOT == True:
            if player.double == True:
                x = player.x + player.bbox_width - 2
            else:
                x = player.x + 10
        if game.LASER_SHOT == True:
            x = player.x + player.bbox_width / 2 + 4
        if game.DOUBLE_LASER_SHOT == True:
            if player.double_laser == True:
                x = player.x + player.bbox_width - 2
            else:
                x = player.x + 10

        ball_sprite = sge.gfx.Sprite(width=self.bullet_size, height=10, origin_x=4, origin_y=4)
        if game.LASER_SHOT == True:
            ball_sprite.width = 1
            ball_sprite.height = 100
            self.bullet_speed = 50
        if game.DOUBLE_LASER_SHOT == True:
            ball_sprite.width = 1
            ball_sprite.height = 100
            self.bullet_speed = 50
        
        ball_sprite.draw_rectangle(0, 0, ball_sprite.width, ball_sprite.height,
                                   fill=game.CITIUS_COLOR)

        super(PlayerBullet, self).__init__(x, player.y, sprite=ball_sprite)

    def event_create(self):
        self.yvelocity = -self.bullet_speed

    def event_step(self, time_passed, delta_mult):
        if self.bbox_bottom < 0:
            self.destroy()
        else:
            # Collision detection only for bullets
            killed = self.collision(other=Kraken)

            if killed:
                killed[0].destroy()
                game.SCORES += + 1
                if game.SCORES > game.HIGHSCORE:
                    game.HIGHSCORE += 1

                DESTROY_SOUND.play()
                self.destroy()
                self.killed = True
        if game.SCORES % 10 == 0 and game.SCORES != 0:
            if game.SCORES == 70:
                self.bullet_speed = self.bullet_speed + 15
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False
            elif game.SCORES < 70:
                self.bullet_speed = self.bullet_speed + 10
                game.UPGRADE = True
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False

        if game.SCORES % 20 == 0 and game.SCORES != 0:
            if game.SCORES >= 100:
                self.bullet_size = self.bullet_size + 0.6
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False
            elif game.SCORES < 80:
                self.bullet_size = self.bullet_size + 0.3
                game.UPGRADE = True
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False

        if game.SCORES % 40 == 0:
            if game.SCORES == 40:
                game.DOUBLE_SHOOT = True
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False
            elif game.SCORES == 80:
                game.TRIPLE_SHOOT = True
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False
            elif game.SCORES == 120:
                game.LASER_SHOT = True
                if self.killed == True:
                    self.upgrade_sound.play()
                self.killed = False
            elif game.SCORES == 160:
                game.DOUBLE_LASER_SHOT = True
                if self.killed >= True:
                    self.upgrade_sound.play()
                self.killed = False
