import pygame
from scripts.utils import Animation
from typing import List
import time


class Player:
    def __init__(self, game, screen, playerlvl, num, range=10, health=100, speed=0.6, damage=[10,0], attack_speed=[0.5,0.5],flip=False):
        self.surf = screen
        self.game = game
        self.pos = [-20,440] if not flip else [1700,440]
        self.enemy_base = 150 if flip else 1500
        self.flip = flip
        self.screen = screen
        self.player_level = playerlvl
        self.num = num
        self.damage = damage
        self.speed = speed
        self.attack_speed = attack_speed
        self.health = health
        self.range = range
        self.outline = None
        self.edge = float("infinity") if self.flip else float("-infinity")
        self.last_attack = time.time()
        self.target = None
        self.method = 0
        #animation attributes
        self.animation : Animation = Animation([self.game.assets['bg']])
        self.action =  ''
        self.set_action('idle')
        

        for point in self.outline:
            if self.flip:
                if point[0] < self.edge:
                    self.edge = point[0]
            else:
                if point[0] > self.edge:
                    self.edge = point[0]                    

        # Movement attributes
        
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

 
    #setting the action attribute for our animation function
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.data[f"{self.player_level + 1}_{self.num + 1}_{self.action}"][0].copy()
            self.outline = self.game.data[f"{self.player_level + 1}_{self.num + 1}_{self.action}"][1]


    #update our position and handle collision based on user input and change the animation
    def update(self, enemies : List["Player"]):
        #set collisions in all directions to be false at the start of the frame
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        #update the frame movement based on the the user input

        for enemy in enemies:
            if (q :=abs((self.edge + self.pos[0]) - (enemy.edge + enemy.pos[0]))) > 150:
                continue
            
            for i, rang in enumerate(self.range):
                if q <= rang:
                    self.target = enemy
                    self.set_action('attack')
                    self.method = i
                    break
        

        for i, rang in enumerate(self.range):
            if abs(self.edge + self.pos[0] - self.enemy_base) <= rang:
                self.target = "base"
                self.method = i
                self.set_action('attack')
                break

        if self.action == 'attack':
            if self.target:
                if self.target == "base":
                    if abs((self.edge + self.pos[0]) - self.enemy_base) <= self.range[self.method]:
                        if (t:=time.time()) - self.last_attack >= self.attack_speed[self.method]:
                            if not self.flip:
                                self.game.enemy_health -= self.damage[self.method]
                            else:
                                self.game.player_health -= self.damage[self.method]
                            self.last_attack = t
                else:
                    if abs((self.edge + self.pos[0]) - (self.target.edge + self.target.pos[0])) <= self.range[self.method]:
                        if (t:=time.time()) - self.last_attack >= self.attack_speed[self.method]:
                            self.target.health -= self.damage[self.method]
                            self.last_attack = t                   

        
        if self.action != "attack":
            self.pos[0] += self.speed if not self.flip else self.speed * -1
            self.set_action('walk')
        if self.animation.done:
            self.set_action('idle')            
        self.animation.update()    


    def render(self, surf, offset = (0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False), (self.pos[0] - offset, self.pos[1]))
