import os
import pygame
import math  



def load_image(path,size=None):
    if size:
        img = pygame.transform.scale(pygame.image.load(path).convert_alpha(),size)
    else:
        img = pygame.image.load(path).convert_alpha()
    return img

def load_images(path,size=None):
    images = []
    for img_name in sorted(os.listdir(path)):
        if img_name.endswith('.jpg') or img_name.endswith('.jpeg') or img_name.endswith('.png') or img_name.endswith('.webp'):
            images.append(load_image(path + '/' + img_name,size=size))
    return images

class Animation:
    def __init__(self, images, dur=5, loop=True):
        self.images = images
        self.dur = dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.dur, self.loop)
    
    def update(self):
        if not self.done:
            if self.loop:
                self.frame = (self.frame + 1) % (self.dur * len(self.images))
            else:
                self.frame = min(self.frame + 1 ,self.dur * len(self.images) -1)
                if self.frame >= self.dur * len(self.images) -1:
                    self.done = True
    
    def img(self) -> pygame.Surface:
        return self.images[int(self.frame/self.dur)]

def load_dir(path, size=None):
    dirs = {}
    for dire in sorted(os.listdir(path)):
        
        dirs[dire] = load_images(path + '/' + dire,size=size)
    return dirs



class Bar:
    def __init__(self, pos, size, health, vertical=True,colors=[(255,0,0),(0,0,0)], text=True):
        self.pos = list(pos)  # Convert position to a list
        self.size = list(size)  # Convert size to a list
        self.max_health = health
        self.vertical = vertical
        self.colors = colors
        self.text = text
        self.font = pygame.font.SysFont("sans", 30)

    def draw(self, surface, health, offset=0):
        # Adjust the size of the bar based on the provided ratio
        ratio = health / self.max_health
        ratio = min(1, ratio)
        size = list(self.size)

        
        if self.vertical:
            size[1] *= ratio
            # Draw the filled rectangle representing the bar
            pygame.draw.rect(surface, self.colors[0], (self.pos[0] - offset, self.pos[1] - size[1], *size))
            if self.text:
                text = self.font.render(str(int(health)), 1, (255,0,0))
                surface.blit(text, (self.pos[0] - offset + 30, self.pos[1] - size[1]))
            # Draw the outline of the bar
            pygame.draw.rect(surface, self.colors[1], (self.pos[0] - offset, self.pos[1] - self.size[1], *self.size), 2)
        else:
            if health > self.max_health:
                size[0] = 0
            else:
                size[0] *= ratio

            # Draw the filled rectangle representing the bar
            pygame.draw.rect(surface, self.colors[0], (self.pos[0] - offset, self.pos[1], *size))
            # Draw the outline of the bar
            pygame.draw.rect(surface, self.colors[1], (self.pos[0] - offset, self.pos[1], *self.size), 2)


class loadbar:
    def __init__(self, pos, size, color=(0,0,0)):
        self.pos = list(pos)  # Convert position to a list
        self.size = list(size)  # Convert size to a list
        self.colors = color
        
        self.font = pygame.font.SysFont("sans", 30)

    def draw(self, surface, ratio, offset=0):
        # Adjust the size of the bar based on the provided ratio
        ratio = min(1, ratio)
        size = list(self.size)
        s = pygame.Surface(self.size, pygame.SRCALPHA)
        s.fill((0,0,255))
        s.set_colorkey((0,0,255))
        s.set_alpha(155)

        
        size[1] *= ratio
        pygame.draw.rect(s, self.colors, (0, 0, *size))
        surface.blit(s,self.pos)



def fps_counter(clock, surf, font):
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("green"))
    surf.blit(fps_t,(0,0))
