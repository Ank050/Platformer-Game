from Settings import *
import pygame as pg
import random
from os import path
vec=pg.math.Vector2


class Spritesheet:
    def __init__(self,filename):
        self.spritesheet=pg.image.load(filename).convert()
        self.spritesheet1=pg.image.load(SPRITESHEET1).convert()
        self.spritesheet2=pg.image.load(SPRITESHEET2).convert()

    def get_image(self,x,y,width,height):
        image=pg.Surface((width,height))
        image.blit(self.spritesheet,(0,0),(x,y,width,height))
        image =pg.transform.scale(image,(width*2,height*2))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self,game):
        self.game=game
        pg.sprite.Sprite.__init__(self)
        self.walking=False
        self.jumping=False
        self.current_frame=0
        self.last_update=0
        self.load_images()
        self.image=self.standing_frames[0]
        self.rect=self.image.get_rect()
        self.rect.center=(WIDTH/2,HEIGHT/2)
        self.pos =vec(WIDTH/2,HEIGHT/2)
        self.vel =vec(0,0)
        self.acc =vec(0,0)
        self.shoot_delay=500
        self.last_shot=pg.time.get_ticks()
        self.direction_r=True
    def load_images(self):
        self.standing_frames=[self.game.spritesheet1.get_image(11,5,30,35),
                              self.game.spritesheet1.get_image(59,5,30,35),
                              self.game.spritesheet1.get_image(107,5,30,35),
                              self.game.spritesheet1.get_image(155,5,30,35),
                              self.game.spritesheet1.get_image(203,5,30,35)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)


        self.walk_frames_r=[self.game.spritesheet.get_image(8,2,36,37),
                            self.game.spritesheet.get_image(55,0,36,37),
                            self.game.spritesheet.get_image(106,3,36,37),
                            self.game.spritesheet.get_image(152,1,36,37),
                            self.game.spritesheet.get_image(202,0,36,37),
                            self.game.spritesheet.get_image(250,2,36,37)]



        self.walk_frames_l=[]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame,True,False))


    def jump(self):
        self.rect.x +=1
        hits=pg.sprite.spritecollide(self,self.game.platforms,False)
        self.rect.x -=1
        if hits:
            self.vel.y=-PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc =vec(0,PLAYER_GRAV)
        keys=pg.key.get_pressed()
        if keys[pg.K_a]:
            self.acc.x=-PLAYER_ACC
            self.direction_r=False
        if keys[pg.K_d]:
            self.acc.x=PLAYER_ACC
            self.direction_r=True
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x)<0.1:
            self.vel.x=0
            self.speedx = 0
        self.pos += self.vel + 0.5*self.acc

        self.rect.center = self.pos
        if self.pos.x > WIDTH or self.pos.x < 0:
            self.game.playing=False
            self.kill()
        self.rect.midbottom=self.pos

    def animate(self):
        now =pg.time.get_ticks()
        if self.vel.x!=0:
            self.walking=True
        else:
            self.walking=False
        if self.walking:
            if now-self.last_update>100:
                self.last_update=now
                self.current_frame=(self.current_frame+1)%len(self.walk_frames_l)
                bottom=self.rect.bottom
                if self.vel.x > 0:
                    self.image=self.walk_frames_r[self.current_frame]
                else:
                    self.image=self.walk_frames_l[self.current_frame]
                self.rect=self.image.get_rect()
                self.rect.bottom=bottom

        if not self.jumping and not self.walking:
            if now -self.last_update > 220:
                self.last_update=now
                self.current_frame=(self.current_frame+1)%len(self.standing_frames)
                bottom=self.rect.bottom
                if self.direction_r==False:
                    self.image=pg.transform.flip(self.standing_frames[self.current_frame],True,False)
                else:
                    self.image=self.standing_frames[self.current_frame]
                self.rect=self.image.get_rect()
                self.rect.bottom=bottom
        self.mask = pg.mask.from_surface(self.image)

class Platform(pg.sprite.Sprite):
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self)
        self.dir=path.dirname(__file__)
        img_dir =path.join(self.dir,'img')
        self.img = pg.image.load(path.join(img_dir, "platform.png")).convert()
        self.img.set_colorkey(BLACK)
        self.image =pg.transform.scale(self.img,(200,50)).convert()
        self.mask = pg.mask.from_surface(self.image)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.speedx=0
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction,img):
        pg.sprite.Sprite.__init__(self)
        self.dir=path.dirname(__file__)
        self.img=img
        self.direction=direction
        img_dir =path.join(self.dir,'img')
        bullet_img = pg.image.load(path.join(img_dir, self.img)).convert()
        if self.direction==False:
            self.image = pg.transform.flip(bullet_img,True,False)
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.centerx=x
            self.rect.midright=y
        else:
            self.image = bullet_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.midleft= y
        self.mask = pg.mask.from_surface(self.image)
        self.speedx = 10

    def update(self):
        if self.direction==False:
            self.rect.x-=self.speedx
            if self.rect.right<0:
                self.kill()
        else:
            self.rect.x += self.speedx
            if self.rect.left>WIDTH:
                self.kill()
class Spaceship(pg.sprite.Sprite):
    def __init__(self,x,y,game):
        self.game=game
        pg.sprite.Sprite.__init__(self)
        self.dir=path.dirname(__file__)
        self.x=x
        self.y=y
        img_dir =path.join(self.dir,'img')
        self.img = pg.image.load(path.join(img_dir, random.choice(ENEMY_PICK))).convert()
        self.image=pg.transform.scale(self.img,(56,56))
        self.image.set_colorkey(BLACK)
        self.mask = pg.mask.from_surface(self.image)
        self.rect=self.image.get_rect()
        self.rect.centerx=self.x
        self.rect.bottom=self.y
        self.pos=vec(self.x,self.y)
        self.last_shot=pg.time.get_ticks()
        if self.game.player.direction_r:
            self.speedx=3+abs(self.game.player.vel.x)
        else:
            self.speedx=3
        if not self.game.player.walking:
            self.speedx=3
    def update(self):
        self.rect.x-=self.speedx
        now=pg.time.get_ticks()
        if self.rect.right < 0:
            self.kill()
        if now - self.last_shot > 1350:
            self.last_shot = now
            laser = Bullet(self.rect.centerx, self.rect.midleft, False, "laserRed.png")
            self.game.all_sprites.add(laser)
            self.game.balls.add(laser)

class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size, game):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.game = game
        self.image = self.game.explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
