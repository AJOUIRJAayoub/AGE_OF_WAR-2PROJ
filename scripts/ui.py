import pygame
from scripts.entities import Player
from scripts.turrets import Turret
from scripts.abilities import AirStrike

class Menu:
    def __init__(self, game, pos, screen) -> None:
        self.dir = ''
        self.game = game
        self.pos = pos
        self.screen : pygame.Surface = screen 
        self.max_level = 5
        self.xps = [0,4000,14000,80000,200000]
        

    def update(self, num):
        if not self.dir:
            if num == 0:
                self.dir = 'troop icons'
            if num == 1:
                self.dir = 'turret icons'
            if num == 2:
                self.game.selling = not self.game.selling
            if num == 3:
                if self.game.turrets_unlocked < len(self.game.slot_cost):
                    price = self.game.slot_cost[self.game.turrets_unlocked]
                    if self.game.player_money >= price:
                        self.game.player_money -= price
                        self.game.turrets_unlocked += 1
                            
            if num == 4:
                index = self.game.player_level 
                if index == self.max_level - 1:
                    return
                if self.game.player_xp >= self.xps[index + 1] :
                    self.game.player_level += 1
                    self.game.maxhealth *= 1.5
                    self.game.player_health *= 1.5    
                    if self.game.player_level == 3 or self.game.player_level == 5:                
                        self.game.ability = AirStrike(pygame.transform.rotate(self.game.assets['special projectiles'][1],90))
                    else:
                        self.game.ability = AirStrike(pygame.transform.rotate(self.game.assets['special projectiles'][self.game.player_level%4],90))
        else:
            if num < 4:
                index = self.game.player_level * 3 + num
                if self.dir == 'troop icons':
                    if self.game.player_level == 5 or num < 3:
                        price = self.game.unit_prices[str(self.game.player_level)][str(num)] 
                        if self.game.player_money >= price and len(self.game.troops_training) < 5 and len(self.game.player_units) < 10:
                            self.game.player_money -= price
                            enemy_index = self.game.enemy_level *3 + num
                            self.game.troops_training.append(Player(self.game, self.screen,self.game.player_level,num, range=[self.game.troop_melee_ranges[index],self.game.troop_ranged_ranges[index]], damage=[self.game.troop_melee_damages[index],self.game.troop_ranged_damages[index]],health=self.game.troop_hps[index],attack_speed=[self.game.troop_melee_speeds[index] ,self.game.troop_ranged_speeds[index]], speed=self.game.troop_speeds[index]))
                            self.game.training = 0
                if self.dir == 'turret icons':
                    
                    price = self.game.turret_prices[str(self.game.player_level)][str(num)]
                    if self.game.player_money >= price :
                        for x in range(self.game.turrets_unlocked+1):
                            pos, turret =list(self.game.turrets.items())[x]
                            if turret:
                                continue
                            
                            self.game.player_money -= price
                            self.game.turrets[pos] =Turret(self.game, self.game.screen, self.game.player_level, num=num, pos=pos,range=self.game.turret_range[index],damage=self.game.turret_damage[index],speed=self.game.turret_speed[index])
                            break
                        
            
    
            if num == 4:
                self.dir = ''
    def render(self, level):
        if not self.dir:
            self.screen.blit(self.game.assets['main'],self.pos)
        else:
            self.screen.blit(self.game.assets[self.dir][level],self.pos)
        
        for i, unit in enumerate(self.game.troops_training):
            pos = (425+ i * 66, 60, 45, 45)
            self.screen.blit(self.game.assets['troop icons'][unit.player_level],pos[:2],(unit.num*52,0,45,45))
        self.screen.blit(self.game.assets['abilities'][self.game.player_level],(1100,100))