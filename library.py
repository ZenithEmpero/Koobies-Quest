import pygame as pg
import random as r
import math as m
import json
import os
from settings import *
from threading import Thread

class Body:
    def __init__(self, main):
        print('Body Class Init')
        self.window = main.window
        self.main = main
        self.player = Player(self)
        self.water = Water(self)

        y1 = r.randint(200, 500)
        y2 = r.randint(200, 500)

        self.obstacle1 = Pillar(self, (1305, y1))
        self.obstacle2 = Pillar(self, (2050, y2))

        self.ui = UI(self)
        self.collision = Collision(self)

        self.score_data = []
        self.score_data_dir = 'data/score.json'

        self.score_data = self.load_game_data(self.score_data_dir)

    def draw(self):
        pass

    def save_game_data(self, data, filename):
        self.check_data_exists(filename)
        with open(filename, "w") as file:
            json.dump(data, file)

    def load_game_data(self, filename):
        self.check_data_exists(filename)
        with open(filename, "r") as file:
            return json.load(file)

    def check_data_exists(self, filename):
        if not os.path.exists(filename):
            with open(filename, "w") as file:
                json.dump([], file)


class UI:
    def __init__(self, body):
        print('UI Class Init')
        pg.font.init()

        self.body = body
        self.main = body.main
        self.player = body.player
        self.window = self.main.window
        
        # VARIABLES
        self.health_pos_cons = (900, 20)
        self.win_size = WIDTH, HEIGHT
        self.mouse_pos = None


        # IMAGES
        self.health_duck = pg.image.load('textures/health_duck.png')
        self.health_skull = pg.image.load('textures/health_skull.png')
        self.health_duck = pg.transform.scale(self.health_duck, (40, 40))
        self.health_skull = pg.transform.scale(self.health_skull, (40, 40))

        self.game_over_img = pg.image.load('textures/game_over.png') #600, 309
        self.game_over_img = pg.transform.scale(self.game_over_img, (480, 247.2))
        self.go_img_dim = self.game_over_img.get_width(), self.game_over_img.get_height()
        self.go_y = ((HEIGHT/2) - 50) - self.go_img_dim[1] / 2 

        self.ta_img = pg.image.load('textures/try_again.png') #549, 130
        self.ta_img = pg.transform.scale(self.ta_img, (274.5, 65))
        self.ta_img_dim = self.ta_img.get_width(), self.ta_img.get_height()
        self.ta_img_rect = self.ta_img.get_rect()
        self.ta_img_rect.x = WIDTH/2 - self.ta_img_dim[0]/2
        self.ta_img_rect.y = self.go_y + 300

        self.hd_dim = self.health_duck.get_width(), self.health_duck.get_height()
        self.hs_dim = self.health_skull.get_width(), self.health_skull.get_height()

        font = 'fonts/Game-Font.ttf'
        self.font = pg.font.Font(font, 200)
        self.font_hs = pg.font.Font(font, 50)

        # FLAGS
        self.mouse_in_ta = False


    def update(self):
        self.mouse_pos_up()
        self.draw()
        self.health()
        self.check_events()
        self.score_update()
        self.score()
        self.highscore()

    def draw(self):
        pass

    def health(self):
        pos_x = self.health_pos_cons[0]
        self.player_health = self.player.health
        j = self.player_health
        for i in range(0, 3):
            if j > 0:
                self.health_draw(self.health_duck, pos_x)
            else:
                self.health_draw(self.health_skull, pos_x)

            pos_x += 60
            j -= 1

        if self.player_health <= 0:
            self.window.blit(self.game_over_img, ((WIDTH/2) - self.go_img_dim[0] / 2, self.go_y))

            if self.ta_img_rect.collidepoint(self.mouse_pos):
                self.ta_img_sc = pg.transform.scale(self.ta_img, (389.4, 78))
                self.mouse_in_ta = True
            else:
                self.ta_img_sc = pg.transform.scale(self.ta_img, (274.5, 65))
                self.mouse_in_ta = False
            self.ta_img_dim = self.ta_img_sc.get_width(), self.ta_img_sc.get_height()
            self.window.blit(self.ta_img_sc, (((WIDTH/2) - self.ta_img_dim[0]/2), self.go_y + 300))
            #pg.draw.rect(self.window, 'white', self.ta_img_rect)

    def health_draw(self, image, x):
        self.window.blit(image, (x, self.health_pos_cons[1]))

    def mouse_pos_up(self):
        self.mouse_pos = pg.mouse.get_pos()

    def check_events(self):
        for event in self.main.events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.player.alive:
                        if self.mouse_in_ta:
                            self.main.menu.running = True
                            self.main.menu.text_start.clicked = False
                            self.main.start = False

    def start_again(self):
        self.player.start_again()
        self.body.obstacle1.start_again()
        self.body.obstacle2.start_again()
        self.body.collision.recent_score_collision = None

    def score_update(self):
        self.main.score = self.player.score

    def score(self):
        if self.player.alive:
            self.text = self.font.render(str(self.player.score), True, 'black')
            x = WIDTH/2 - (self.text.get_width() / 2)
            self.window.blit(self.text, (x + 5, 60 + 5))
            self.text = self.font.render(str(self.player.score), True, 'yellow')
            x = WIDTH/2 - (self.text.get_width() / 2)
            self.window.blit(self.text, (x, 60))
            

    def highscore(self):
        text = self.font_hs.render('HIGHSCORES', True, 'black')
        self.window.blit(text, (10 + 3, 10 + 3))
        j =40
        a = 1
        for i in self.body.score_data:
            text = self.font_hs.render(f'[{a}] {i}', True, 'black')
            self.window.blit(text, (20 + 3, j + 3))
            j += 25
            a += 1

        text = self.font_hs.render('HIGHSCORES', True, 'yellow')
        self.window.blit(text, (10, 10))
        j =40
        a = 1
        for i in self.body.score_data:
            text = self.font_hs.render(f'[{a}] {i}', True, 'yellow')
            self.window.blit(text, (20, j))
            j += 25
            a += 1


class Pillar:
    def __init__(self, body, pos) -> None:
        self.body = body
        self.main = body.main
        self.window = self.main.window
        self.player = body.player
        self.coordinate = pos
        self.pos = pos
        self.gap = 670
        self.speed = obstacle_speed
        self.pillar_img = pg.image.load('textures/pillar.png')
        self.pillar_img = pg.transform.scale(self.pillar_img, (189, 483))
        self.pillar_img_dim = self.pillar_img.get_width(), self.pillar_img.get_height()

        self.pillar2_img = pg.image.load('textures/pillar2.png')
        self.pillar2_img = pg.transform.scale(self.pillar2_img, (189, 483))

        self.top_pillar_img = pg.transform.rotate(self.pillar_img, 180)
        self.top_pillar2_img = pg.transform.rotate(self.pillar2_img, 180)

        self.pillar_used = self.pillar_img
        self.top_pillar_used = self.top_pillar_img

        self.start = False
        #Thread(target= self.speed_increase).start()

    def update(self):
        self.movement()
        self.window.blit(self.pillar_used, (self.coordinate[0], self.coordinate[1]))
        self.window.blit(self.top_pillar_used, (self.coordinate[0], self.coordinate[1] - self.gap))

    def movement(self):
        if self.player.alive and not self.main.menu.running:
            if self.coordinate[0] < -200:
                self.coordinate = (1300, r.randint(200, 520))
                self.body.collision.recent_player_collision = None
                self.body.collision.recent_score_collision = None

                for i in range(0, 2):
                    if i == 0:
                        self.pillar_used = self.pillar_img
                    elif i == 1:
                        self.pillar_used = self.pillar2_img
                for i in range(0, 2):
                    if i == 0:
                        self.top_pillar_used = self.top_pillar_img
                    elif i == 1:
                        self.top_pillar_used = self.top_pillar2_img

            else:
                x = self.coordinate[0] - self.speed * self.main.delta_time
                self.coordinate = x, self.coordinate[1]

    def speed_increase(self):
        while self.main.running and self.player.alive and not self.main.menu.running:
            pg.time.wait(1000)
            self.speed += .001

    def start_again(self):
        self.coordinate = self.pos
        self.speed = obstacle_speed


class Player:
    def __init__(self, body):
        print('Player Class Init')
        self.player_pos = (200, 100)
        self.body = body
        self.main = body.main
        self.health = 3
        self.alive = True
        self.score = 0
        self.duck_image = pg.image.load('textures/duck.png')
        self.duck_image = pg.transform.scale(self.duck_image, (60, 60))
        self.or_duck_image = self.duck_image
        self.duck_rect = self.or_duck_image.get_rect()


        self.duck_dim = self.duck_image.get_width(), self.duck_image.get_height()

        self.x = self.player_pos[0]
        self.y = self.player_pos[1]
        self.sm = 0
        self.sm_y = 0

        self.drag = 0

        self.rise = False
        self.rot = 0
        self.rot_x = 0
        self.angle = 0

        self.damage_animation = False
        self.show_image = True
        self.da = 0

        # GAME OVER Flags and Variables
        self.go_sec = -200
        self.velocity = 0
        self.acceleration = 0.1
        self.go_down = False
        self.go_val = 0
        self.score_updated = False


    def draw(self):
        #pg.draw.circle(self.main.window, 'red', self.player_pos, 25)
        self.sin_motion()
        self.rotate_image()

        if self.show_image:
            self.main.window.blit(self.duck_image, (self.player_pos[0] - self.rotated_duck_rect.width / 2, self.player_pos[1] - self.rotated_duck_rect.height / 2))
        #pg.draw.circle(self.main.window, 'red', self.player_pos, 2)
        self.controls()

        self.check_if_alive()
        self.play_damage_animation(0.25)

    def controls(self):
        if self.alive:
            keys = pg.key.get_pressed()
            speed = self.drag * player_speed
            if keys[pg.K_SPACE]:
                self.drag -= 0.1
                if self.drag < -1:
                    self.drag = -1
            else:
                self.drag += 0.1
                if self.drag > 1:
                    self.drag = 1

            self.y += speed * self.main.delta_time
            if self.y > 565:
                self.y = 565
            if self.y < 35:
                self.y = 35
            self.player_pos = (self.x, self.y)

    def rotate_image(self):
        self.duck_image = pg.transform.rotate(self.or_duck_image, self.rot)
        self.rotated_duck_rect = self.duck_image.get_rect()
        self.rotated_pos = self.rotated_duck_rect.center

        if self.health >= 1:
            self.rot = m.sin(self.rot_x) * 14
            self.rot_x += 0.005 * self.main.delta_time
        else:
            self.angle += .6 * self.main.delta_time
            self.rot = self.angle

    def sin_motion(self):
        if self.health >= 1:
            self.sm_y = self.player_pos[1]
            self.sm += .004 * self.main.delta_time
            self.sm_y += m.sin(self.sm) * 6 #* self.main.delta_time
            self.player_pos = (self.player_pos[0], self.sm_y)

    def check_if_alive(self):
        if self.health <= 0:
            self.alive = False
            self.game_over()

            if not self.score_updated:
                self.update_score_data()
        else:
            self.original_pos = self.player_pos
            self.alive = True


    def play_damage_animation(self, x):
        if self.damage_animation:
            self.da += 0.05 * self.main.delta_time
            self.da_sin = m.sin(self.da)
            if self.da_sin > 0:
                self.show_image = False
            else:
                self.show_image = True
        else:
            self.show_image = True


    def game_over(self):
        if self.velocity == 0:
            self.go_down = False
        if not self.go_down:
            self.velocity = -3

            if self.go_val > 15:
                self.go_down = True

            self.go_val += 1
        else:
            self.velocity += 0.1

            if self.velocity > 6:
                self.velocity = 6
            
        speed = self.velocity * .1
        self.player_pos = self.original_pos[0], self.player_pos[1] + (speed * self.main.delta_time)

    def start_again(self):
        self.health = 3
        self.velocity = 0
        self.go_val = 0
        self.angle = 0
        self.score = 0
        self.score_updated = False

    def update_score_data(self):
        score_data = self.body.score_data

        score_data.append(self.score)
        if len(score_data) > 3:
            score_data.sort()
            score_data.reverse()
            score_data.pop(-1)

        self.score_updated = True
        score_data.sort()
        score_data.reverse()
        self.body.score_data = score_data
        self.body.save_game_data(self.body.score_data, self.body.score_data_dir)


class Water:
    def __init__(self, body):
        print('Water Class Init')
        self.body = body
        self.main = body.main
        self.window = self.main.window
        self.player = body.player
        self.water_pos = (0, 400)

        self.x = 0
        self.y = self.water_pos[1]

    def draw(self):
        self.draw_water_rect()

    def draw_water_rect(self):
        #self.sin_wave()
        if not self.player.alive:
            if self.water_pos[1] > -100:
                self.water_pos = (0, self.water_pos[1] + (.1 * self.main.delta_time))
        else:
            self.water_pos = (0, self.player.player_pos[1] + 14)

        self.water_rect = pg.Surface((1200, 1000), pg.SRCALPHA)
        self.water_rect.fill((0, 0, 255, 100))
        self.window.blit(self.water_rect, self.water_pos)


    def sin_wave(self):
        if self.player.health >= 1:
            self.y = self.body.player.player_pos[1] + 14
            self.x += .004 * self.main.delta_time
        if self.y > -100:
            self.y += m.sin(self.x) * 6 #* self.main.delta_time
            self.water_pos = (0, self.y)

class Collision:
    def __init__(self, body):
        print('Collision Class Inir')
        self.body = body
        self.main = body.main
        self.player = body.player
        self.ob1 = body.obstacle1
        self.ob2 = body.obstacle2
        self.window = self.main.window


        self.recent_player_collision = None
        self.recent_score_collision = None

    def update(self):
        self.position_collision_rect()
        #self.draw()
        self.detect_collision()

    def draw(self):
        pg.draw.rect(self.window, hitbox_color, self.player_rect, width=4)
        pg.draw.rect(self.window, hitbox_color, self.ob1_rect, width=4)
        pg.draw.rect(self.window, hitbox_color, self.ob1_rect_top, width=4)
        pg.draw.rect(self.window, hitbox_color, self.ob2_rect, width=4)
        pg.draw.rect(self.window, hitbox_color, self.ob2_rect_top, width=4)

        pg.draw.rect(self.window, 'green', self.ob1_score_rect, width=4)
        pg.draw.rect(self.window, 'green', self.ob2_score_rect, width=4)

    def position_collision_rect(self):
        # PLAYER COLLISION
        size_reduction_rate = .4
        reduced_size = self.player.duck_dim[0] - (self.player.duck_dim[0] * size_reduction_rate), self.player.duck_dim[1] - (self.player.duck_dim[1] * size_reduction_rate)
        adjust_pos = self.player.player_pos[0] - (reduced_size[0] // 2), self.player.player_pos[1] - (reduced_size[1] // 2)
        self.player_rect = pg.Rect(adjust_pos[0], adjust_pos[1], reduced_size[0], reduced_size[1])

        # OBSTACLE 1 COLLISION
        size = self.ob1.pillar_img_dim[0], self.ob1.pillar_img_dim[1]
        ob1_pos = self.ob1.coordinate[0], self.ob1.coordinate[1]
        self.ob1_rect = pg.Rect(ob1_pos[0], ob1_pos[1], size[0], size[1])
        self.ob1_rect_top = pg.Rect(ob1_pos[0], ob1_pos[1] - (self.ob1.gap), size[0], size[1])
        self.ob1_score_rect = pg.Rect(ob1_pos[0] + 100, ob1_pos[1] - 170, 90, 150)

        # OBSTACLE 2 COLLISION
        size = self.ob2.pillar_img_dim[0], self.ob2.pillar_img_dim[1]
        ob2_pos = self.ob2.coordinate[0], self.ob2.coordinate[1]
        self.ob2_rect = pg.Rect(ob2_pos[0], ob2_pos[1], size[0], size[1])
        self.ob2_rect_top = pg.Rect(ob2_pos[0], ob2_pos[1] - (self.ob2.gap), size[0], size[1])
        self.ob2_score_rect = pg.Rect(ob2_pos[0] + 100, ob2_pos[1] - 170, 90, 150)

        self.ob1_rects = [self.ob1_rect, self.ob1_rect_top]
        self.ob2_rects = [self.ob2_rect, self.ob2_rect_top]


    def detect_collision(self):
        for i in self.ob1_rects:
            if self.recent_player_collision != 1:
                if self.player_rect.colliderect(i):
                    self.player.health -= 1
                    self.main.forg_audio.play()
                    if self.player.health >= 1:
                        Thread(target= self.reverse_damage_animation).start()
                    self.recent_player_collision = 1

        for i in self.ob2_rects:
            if self.recent_player_collision != 2:
                if self.player_rect.colliderect(i):
                    self.player.health -= 1
                    self.main.forg_audio.play()
                    if self.player.health >= 1:
                        Thread(target= self.reverse_damage_animation).start()
                    self.recent_player_collision = 2

        if self.recent_score_collision != 1:
            if self.player_rect.colliderect(self.ob1_score_rect):
                self.player.score += 1
                self.recent_score_collision = 1
        
        if self.recent_score_collision != 2:
            if self.player_rect.colliderect(self.ob2_score_rect):
                self.player.score += 1
                self.recent_score_collision = 2

    def reverse_damage_animation(self):
        self.player.damage_animation = True
        pg.time.wait(1000)
        self.player.damage_animation = False