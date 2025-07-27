import pygame
from scripts.utils import Animation
import math
from typing import List
import time


class Turret:
    def __init__(self, game, screen, playerlvl, num, pos, range=10, damage=10, speed=0.5,flip=False):
        self.surf = screen
        self.game = game
        self.pos = pos
        self.flip = flip
        self.screen = screen
        self.player_level = playerlvl
        self.num = num
        self.damage = damage
        self.attack_speed = speed
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




        #get the rect of the player for the purposes of collision detection
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

 
    #setting the action attribute for our animation function
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.turret_data[f"{self.player_level*3+self.num+1}_{self.action}"][0].copy()
            self.outline = self.game.turret_data[f"{self.player_level*3+self.num+1}_{self.action}"][1]


    #update our position and handle collision based on user input and change the animation
    def update(self, enemies : List["Turret"]):
        #set collisions in all directions to be false at the start of the frame
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        distance = float('infinity')
        #update the frame movement based on the the user input

        for enemy in sorted(enemies, key=lambda x:x.pos[0],reverse=True):
            if (distance:=math.sqrt(math.pow(abs((self.edge + self.pos[0]) - (enemy.edge + enemy.pos[0])),2)+math.pow(abs((self.edge + self.pos[1]) - (enemy.edge + enemy.pos[1])),2))) <= self.range:
                    self.target = enemy
                    self.set_action('attack')

        if self.action == 'attack':
            if self.target:
                if distance <= self.range:
                    if (t:=time.time()) - self.last_attack >= self.attack_speed:
                        self.target.health -= self.damage
                        self.last_attack = t                   

        if self.animation.done:
            self.set_action('idle')            
        self.animation.update()    


    def render(self, surf, offset = (0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False), (self.pos[0] - offset, self.pos[1]))
