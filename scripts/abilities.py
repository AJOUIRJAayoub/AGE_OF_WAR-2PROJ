import math
import random
import pygame


class AirStrike:
    def __init__(self, img, damage=120,width = 1200, count=20) -> None:
        self.count = count
        self.img = pygame.transform.scale2x(pygame.transform.rotate(img, -90))
        self.damage = damage
        self.width = width
        self.rocks = self.generate_rocks()

    def generate_rocks(self) -> list[dict]:
        rocks = []
        for i in range(self.count):
            angle = math.radians(random.randint(2650,2750)/10)
            pos = [random.randint(100,1400), random.randint(100,1500)*-1]
            speed = random.randint(500,600)/100
            speed = (math.cos(angle)*speed, -math.sin(angle)*speed)
            rect = pygame.Rect(*pos, self.img.get_width(), self.img.get_height()/2)
            rock = {
                'angle' : math.degrees(angle),
                'speed' : speed,
                'rect' : rect,
            }
            rocks.append(rock)
        return rocks
    
    def update(self, floor,enemies):
        for rock in self.rocks:
            rock['rect'][0] += rock['speed'][0]
            rock['rect'][1] += rock['speed'][1]
            if rock['rect'][1] >= floor:
                self.rocks.remove(rock)

        for enemy in enemies:
            for rect in self.rocks:
                rect = rect['rect']
                if rect[1] < 250:
                    continue
                for point in enemy.outline:
                    if rect.collidepoint((point[0]+enemy.pos[0],point[1]+enemy.pos[1])):
                        enemy.health -= self.damage

        if not self.rocks:
            return True


    def render(self, surface, camera=0):
        for rock in self.rocks:
            surface.blit(pygame.transform.rotate(self.img, rock['angle']), (rock['rect'][0] - camera, rock['rect'][1]))
