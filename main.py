import pygame
import sys
import json
import random
import time
import math
from scripts.utils import load_dir, load_images, load_image, Bar as HealthBar, Animation, loadbar
from scripts.ui import Menu
from scripts.abilities import AirStrike
from scripts.entities import Player

class Main:
    def __init__(self):
        pygame.mixer.pre_init()
        pygame.init()
        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)
        self.width = 1200
        self.height = 550
        self.difficulty = 1
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Age of War")
        self.menu = Menu(self, (900,30), self.screen)
        optimization = 1 #increase to increase performance at the price of more accurate collisions
        self.slot_cost =  [1000, 3000, 7500 ]
        self.turret_damage =  [12, 5, 25, 40, 50, 125, 30, 70, 100, 70, 100, 60, 100, 40, 60 ]
        self.turret_range = [350, 300, 380, 400, 300, 50, 500, 500, 500, 500, 500, 500, 400, 500, 550 ]
        self.turret_speed = [0.8, 0.25, 1.37, 2.47, 2.47, 1.92, 1.12, 2, 2, 1.12, 1, 0.5, 1, 0.25, 0.25]
        self.troop_hps = [ 55, 42, 160, 100, 80, 300, 200, 160, 600, 350, 300, 1200, 1000, 800, 3000, 4000 ]
        self.troop_melee_damages = [ 16, 10, 40, 35, 20, 60, 79, 40, 120, 100, 60, 300, 250, 130, 600, 400 ]
        self.troop_ranged_damages = [ 0, 8, 0, 0, 14, 0, 0, 20, 0, 0, 30, 0, 0, 80, 0, 400 ]
        self.troop_melee_ranges = [20, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25, 20, 20, 20, 20, 20 ]
        self.troop_ranged_ranges = [0, 100, 0, 0, 130, 0, 0, 130, 0, 0, 130, 0, 0, 110, 0, 130 ]
        self.troop_melee_speeds = [1, 1, 1.12, 2.47/2, 2.47/2, 1.30, 1.05, 1.15, 1.95, 0.75, 0.52, 1.57, 0.92, 0.7, 2.25, 0.7]
        self.troop_ranged_speeds = [0, 0.8, 0, 0, 1, 0, 0, 1.15, 0, 0, 0.52, 0, 0, 0.35, 0, 0.35]
        self.troop_speeds = [0.6, 0.5, 0.7, 0.6, 0.6, 0.8, 0.7, 0.7, 0.7, 0.7, 0.6, 0.5, 0.7, 0.7, 0.5, 0.8]
        self.turret_spot = [20, 68, 116, 164]
        r = 1.1
        self.turrets_unlocked = 0
        bg_size = [1577*r, 504*r]
        self.bases = [ 150 , 1550]
        ac = ['idle' , 'attack', 'walk']
        self.data = {f"{str(i+1)}_{str(x+1)}_{ac[n]}" : (Animation([load_image(f'assets/imgs/sprites/troops/{str(i+1)} {str(x+1)}.png')],loop=False if n==1 else True),pygame.mask.from_surface(Animation([load_image(f'assets/imgs/sprites/troops/{str(i+1)} {str(x+1)}.png')]).img()).outline(every=optimization)) for i in range(5) for x in range(3) for n in range(3)}

        ac.pop()
        self.turret_data = {f"{str(i+1)}_{ac[n]}" : (Animation([load_image(f"assets/imgs/sprites/turrets/{i+1}.png")],loop=False if n==1 else True),pygame.mask.from_surface(Animation([load_image(f'assets/imgs/sprites/turrets/{i+1}.png')]).img()).outline(every=optimization)) for i in range(15) for n in range(2)}
        audio = pygame.mixer.Sound('assets/audio.mp3')        
        audio.set_volume(0.1)
        audio.play(-1) #comment out to remove audio
        self.assets = load_dir('assets/imgs/sprites')
        
        self.assets['bg'] = load_image('assets/1.png', size=bg_size)
        self.assets['main'] = pygame.transform.scale_by(load_image('assets/1 1.png'),1.3)
        for i , img in enumerate(self.assets['troop icons']):
            self.assets['troop icons'][i] = pygame.transform.scale_by(img,1.3)
        for i , img in enumerate(self.assets['turret icons']):
            self.assets['turret icons'][i] = pygame.transform.scale_by(img,1.3)            
        self.player_level = self.enemy_level = 0
        self.player_xp = self.enemy_xp = 0
        self.player_money = 150
        with open('assets/prices.json', 'r') as f:
            stats = json.load(f)
        for i , img in enumerate(self.assets['abilities']):
            self.assets['abilities'][i] = pygame.transform.scale(img,(50,50))  

        for i , img in enumerate(self.assets['troops']):
            self.assets['troops'][i] = Animation([img])
        self.assets['bases'][2] = pygame.transform.scale_by(self.assets['bases'][2],1.4)
        
        self.unit_prices = stats[0]
        self.turret_prices = stats[1]
        self.player_units = []
        self.enemy_units = []
        self.troops_training = []
        self.ability = AirStrike(self.assets['special projectiles'][self.player_level])
        self.training = 40
        self.maxhealth = 500
        self.enemy_health = self.maxhealth
        self.player_health = self.maxhealth
        self.selling = False
        t = {(80,370) : None}
        t.update({(80,360-(self.turret_spot[x])*1-20) : None for x in range(3)})
        self.turrets = t
        self.home()

    def home(self):
        sfont = pygame.font.SysFont("sans", 30)
        font = pygame.font.SysFont("sans", 36)
        d = ['easy','normal','hard','insane']
        clicking = False
        while True:
            self.screen.fill((0,0,0))    
            self.screen.blit(self.assets['bg'],(-200,0))
            text = font.render('Difficulties',True,(0,0,0))
            self.screen.blit(text,(500,200))
            rects = []
            mpos = pygame.mouse.get_pos()
            for i ,word in enumerate(d):
                text = sfont.render(word,True,(0,0,0))
                pos = (540,250+i*50)
                self.screen.blit(text,(pos))
                rect = pygame.Rect(*pos,*text.get_size())
                if rect.collidepoint(mpos) and clicking:
                    self.difficulty = i+1
                    self.reset()
                rects.append(rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        clicking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == pygame.BUTTON_LEFT:
                        clicking = False                        

            self.clock.tick(60)
            pygame.display.update()

    def won(self):
        font = pygame.font.SysFont("sans", 30)
        while True:
            self.screen.fill((0,0,0))    
            self.screen.blit(self.assets['bg'],(-200,0))
            text = font.render('you have won',True,(0,0,0))
            self.screen.blit(text,(500,200))
            text = font.render('left click to restart',True,(0,0,0))
            self.screen.blit(text,(520,250))     
            text = font.render('menu',True,(0,0,0))
            pos =(545,300)
            self.screen.blit(text,pos)                 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if pygame.Rect(*pos,*text.get_size()).collidepoint(pygame.mouse.get_pos()):
                            self.home()
                        self.reset()


            self.clock.tick(60)
            pygame.display.update()

    def lost(self):
        font = pygame.font.SysFont("sans", 30)
        while True:
            self.screen.fill((0,0,0))    
            self.screen.blit(self.assets['bg'],(-200,0))
            text = font.render('you have lost',True,(0,0,0))
            self.screen.blit(text,(500,200))
            text = font.render('left click to restart',True,(0,0,0))
            self.screen.blit(text,(480,250))     
            text = font.render('menu',True,(0,0,0))
            pos =(545,300)
            self.screen.blit(text,pos)                 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if pygame.Rect(*pos,*text.get_size()).collidepoint(pygame.mouse.get_pos()):
                            self.home()
                        self.reset()

            self.clock.tick(60)
            pygame.display.update()

    
    def reset(self):
        self.player_units = []
        self.enemy_units = []
        self.troops_training = []
        self.ability = AirStrike(self.assets['special projectiles'][self.player_level])
        self.training = 40
        self.maxhealth = 500
        self.enemy_health = self.maxhealth
        self.player_health = self.maxhealth
        self.player_level = self.enemy_level = 0
        self.player_xp = self.enemy_xp = 0
        self.player_money = 150
        t = {(80,370) : None}
        t.update({(80,360-(self.turret_spot[x])*1-20) : None for x in range(3)})
        self.turrets = t
        self.selling = False
        self.turrets_unlocked = 0
        self.run()

    def run(self):
        font = pygame.font.SysFont("sans", 30)
        sfont = pygame.font.SysFont("sans", 24)
        camera = 0

        healthbar1 = HealthBar((50,290),(25, 200),self.maxhealth)
        healthbar2 = HealthBar((1550,290),(25, 200),self.maxhealth)
        training_bar = HealthBar((self.screen.get_width()//2 - 270,30),(500, 10),30,vertical=False)
        self.last_airstrike = 0
        self.load_bar = loadbar((1100,100),(50,50))
        activate = False
        movement = [False, False]
        speed = 3
        clicking = False
        delay = 40
        last_trained = time.time()
        spawn_delay = random.randint(100,2000)/1000
        xps = [0,4000,14000,80000,200000]

        while True:
            self.screen.fill((0,0,0))
            self.screen.blit(self.assets['bg'],(-camera,0))
            camera += int(movement[1] - movement[0]) * speed
            self.training += 1
            self.training = max(0, self.training)
            camera = max(40, camera)
            camera = min(self.assets['bg'].get_width() - 70 - self.screen.get_width(), camera)
            enemy_loc = (1500 - camera,360)
            player_loc = (-camera-20,360)
            mpos = pygame.mouse.get_pos()
            
            if self.enemy_health < 1:
                self.won()
            if self.player_health < 1:
                self.lost()
            
            
            if self.training >= 60 and len(self.troops_training) > 0:
                self.player_units.append(self.troops_training.pop(0))
                self.training = 0
            
            
            self.screen.blit(pygame.transform.flip(self.assets['bases'][self.enemy_level*2 + 1],True,False),enemy_loc)

            self.screen.blit(self.assets['bases'][self.player_level*2 + 1],player_loc)
            for unit in self.enemy_units:
                unit.update(self.player_units)
                if unit.health < 1:
                    self.enemy_units.remove(unit)
                    self.player_money += self.unit_prices[str(unit.player_level)][str(unit.num)] * 2
                    self.player_xp += self.unit_prices[str(unit.player_level)][str(unit.num)] * 3.5
                unit.render(self.screen, camera)

            for unit in self.player_units:
                unit.update(self.enemy_units)
                if unit.health < 1:
                    self.player_units.remove(unit)
                    self.enemy_xp += self.unit_prices[str(unit.player_level)][str(unit.num)] * 12
                unit.render(self.screen, camera)
            for i in range(self.turrets_unlocked):
                pos = (player_loc[0]+100,player_loc[1]-self.turret_spot[i]*1-20)

                img = self.assets['bases'][self.player_level*2]
                self.screen.blit(img,pos)
            for i in range(self.turrets_unlocked+1):
                pos = (player_loc[0]+100,player_loc[1]-self.turret_spot[i]*1-20)

                img = self.assets['bases'][self.player_level*2]

                if self.selling:
                    rect = pygame.Rect([pos[0],pos[1]+75,img.get_width(),img.get_height()//2+10])
                    pygame.draw.rect(self.screen, (255,0,0),rect,2)
                    if rect.collidepoint(mpos) and clicking:
                        k = list(self.turrets.keys())[i]
                        if self.turrets[k]:
                            index = self.turrets[k].num + self.turrets[k].player_level * 3
                            self.player_money += self.turret_prices[str(index//3)][str(index%3)]
                            self.turrets[k] = None


            for pos, turret in self.turrets.items():
                if turret:
                    turret.update(self.enemy_units)
                    turret.render(self.screen, camera)
            healthbar1.draw(self.screen, self.player_health, camera)
            healthbar2.draw(self.screen, self.enemy_health , camera)            
            training_bar.draw(self.screen, self.training, 0)
            self.menu.render(self.player_level)


            text = font.render(f"Exp : {int(self.player_xp)}",True,(255,255,0))
            self.screen.blit(text, (22, 18))

            text = font.render(f"Gold : {int(self.player_money)}",True,(0,0,0))
            self.screen.blit(text, (18, 52))


            for i in range(5):
                rect = pygame.Rect(self.menu.pos[0]+ i * 52, self.menu.pos[1], 45, 45)
                if rect.collidepoint(mpos):
                    if clicking:
                        self.menu.update(i)
                        clicking = False
                if not self.menu.dir:
                    if self.turrets_unlocked < len(self.slot_cost):
                        price = self.slot_cost[self.turrets_unlocked]
                        text = sfont.render(str(price),True,(255,255,0))
                        self.screen.blit(text,(self.menu.pos[0]+ 3 * 52, self.menu.pos[1] + 50))                        
                if i < 3 or (i < 4  and self.player_level == 5):
                    if self.menu.dir == 'troop icons':
                        text = sfont.render(str(self.unit_prices[str(self.player_level)][str(min(i,2))]),True,(255,255,0))
                        self.screen.blit(text,(self.menu.pos[0]+ i * 52, self.menu.pos[1] + 50))                        
            
            self.enemy_xp += 1 * (self.enemy_level+1)
            for i in range(5):
                rect = pygame.Rect(425+ i * 66, 60, 45, 45)
                pygame.draw.rect(self.screen, (0,0,0), rect, 3)
            rect = pygame.Rect(*(1100,100),50,50)
            if rect.collidepoint(mpos):
                if clicking:
                    if (t := time.time()) - self.last_airstrike > delay:
                        self.last_airstrike = t
                        activate = True            
                        clicking = False
       
            if activate:
                    line = 60
                    if self.ability.update(self.height - line,self.enemy_units):
                        self.ability = AirStrike(pygame.transform.rotate(self.assets['special projectiles'][self.player_level%4],90))
                        activate = False
                    self.ability.render(self.screen, camera)


            self.load_bar.draw(self.screen,1-(time.time()-self.last_airstrike)/delay)    
            
            if time.time() - last_trained > spawn_delay:
                if self.enemy_xp:
                    r = (self.enemy_xp+0.01)/xps[self.enemy_level+1]
                else:
                    r = 0
                num = random.randint(0,2000)/1000/math.sqrt(self.difficulty)
                num *= r
                num = round(num)
                num = min(2,num)
                enemy_index = self.enemy_level *3 + num
                self.enemy_units.append(Player(self, self.screen,self.enemy_level,num, range=[self.troop_melee_ranges[enemy_index],self.troop_ranged_ranges[enemy_index]], damage=[self.troop_melee_damages[enemy_index]*math.sqrt(self.difficulty),self.troop_ranged_damages[enemy_index]*math.sqrt(self.difficulty)],health=self.troop_hps[enemy_index]*math.sqrt(self.difficulty),attack_speed=[self.troop_melee_speeds[enemy_index]*math.sqrt(self.difficulty) ,self.troop_ranged_speeds[enemy_index]*math.sqrt(self.difficulty)],speed=self.troop_speeds[enemy_index], flip=True))
                last_trained = time.time()
                spawn_delay = random.randint(10,6000)/1000/math.sqrt(self.difficulty)

                                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        clicking = True  
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        clicking = False     
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        movement[1] = False        

        
            if self.enemy_xp >= 200000:
                
                    self.enemy_level = 4
            elif self.enemy_xp >= 80000:
                
                    self.enemy_level = 3          
            elif self.enemy_xp >= 14000:
                
                    self.enemy_level = 2
            elif self.enemy_xp >= 4000:
                    self.enemy_level = 1



            self.clock.tick(60)
            pygame.display.update()

game = Main()