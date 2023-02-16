
import pygame as pg
import random
from Settings import *
from sprites import *
from os import path
from pygame import mixer
from tkinter import *
import mysql.connector

pg.mixer.init()
pg.mixer.music.load('bgmusic.wav')
pg.mixer.music.play(-1)


class Game:


    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.bg=pg.transform.scale(pg.image.load("bg4.png"),(WIDTH,HEIGHT))
        self.startbg=pg.image.load("startbg2.png")
        self.endbg=pg.image.load('game over.png')

        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.a=0
        self.font_name=pg.font.match_font(FONT_NAME)
        self.load_data()
        self.score=0

    def load_data(self):
        self.dir=path.dirname(__file__)
        img_dir =path.join(self.dir,'img')
        with open(path.join(self.dir,HS_FILE),'r')as f:
            try:
                self.highscore =int(f.read())
            except:
                self.highscore=0
        self.spritesheet=Spritesheet(path.join(img_dir,SPRITESHEET))
        self.spritesheet1=Spritesheet(path.join(img_dir,SPRITESHEET1))
        self.spritesheet3=Spritesheet(path.join(img_dir,SPRITESHEET3))
        self.explosion_anim = {}
        self.explosion_anim['lg'] = []
        self.explosion_anim['sm'] = []
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img = pg.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey(BLACK)
            img_lg = pg.transform.scale(img, (75, 75))
            self.explosion_anim['lg'].append(img_lg)
            img_sm = pg.transform.scale(img, (32, 32))
            self.explosion_anim['sm'].append(img_sm)
            filename = 'sonicExplosion0{}.png'.format(i)
            img = pg.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey(BLACK)
    def new(self):
        self.score=0
        self.all_sprites = pg.sprite.Group()
        self.platforms=pg.sprite.Group()
        self.bullets=pg.sprite.Group()
        self.balls=pg.sprite.Group()
        self.enemies=pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for self.plat in PLATFORM_LIST :
            self.p=Platform(*self.plat)
            self.all_sprites.add(self.p)
            self.platforms.add(self.p)
            self.ship=Spaceship(self.p.rect.centerx,self.p.rect.top,self)
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        a=0
        self.all_sprites.update()
        hits=pg.sprite.spritecollide(self.player,self.platforms,False)
        if hits:
            self.player.pos.y=hits[0].rect.top
            self.player.vel.y=0
        if self.player.rect.left>= WIDTH/2:
            self.player.pos.x -= abs(self.player.vel.x)
            for plat in self.platforms:
                plat.rect.x -= abs(self.player.vel.x)
                if plat.rect.left<=-10 :
                    plat.kill()
                    self.score +=10
        if self.player.rect.bottom>HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.x -= 30
                if sprite.rect.bottom<600:
                    sprite.kill()
        if len(self.platforms)==0:
            self.playing=False
        hits=pg.sprite.spritecollide(self.player,self.enemies,True,pg.sprite.collide_mask)
        if hits:
            for hit in hits:
                expl_large=Explosion(hit.rect.center, 'lg',self)
                self.all_sprites.add(expl_large)

        hits=pg.sprite.spritecollide(self.player,self.balls,False,pg.sprite.collide_mask)
        if hits:
            self.playing=False
        hits=pg.sprite.groupcollide(self.bullets,self.enemies,True,True,pg.sprite.collide_mask)
        if hits:
            self.score+=20
            for hit in hits:
                expl_large=Explosion(hit.rect.center, 'lg',self)
                self.all_sprites.add(expl_large)

        hits=pg.sprite.groupcollide(self.bullets,self.balls,True,True,pg.sprite.collide_mask)
        for hit in hits:
            expl_small=Explosion(hit.rect.center, 'sm',self)
            self.all_sprites.add(expl_small)
        while len(self.platforms)<=3:
            a=WIDTH+150+a
            self.p=Platform(a,random.randrange(300,470))
            self.platforms.add(self.p)
            self.all_sprites.add(self.p)
            n=random.randint(0,2)
            for i in range(n):
                self.ship=Spaceship(a,random.randrange(300,430),self)
                self.enemies.add(self.ship)
                self.all_sprites.add(self.ship)

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.player.last_shot > self.player.shoot_delay:
            self.player.last_shot = now
            if self.player.direction_r==False:
                bullet= Bullet(self.player.rect.centerx, self.player.rect.midleft,self.player.direction_r,"laserBlue.png")
            else:
                bullet = Bullet(self.player.rect.centerx, self.player.rect.midright,self.player.direction_r,"laserBlue.png")
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                pg.quit()
            if event.type==pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.player.jump()
                if event.key == pg.K_SPACE:
                    self.shoot()
    def draw(self):
        def screenone(x,y):
                self.screen.blit(self.bg,(x,y))
        screenone(0,0)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score),50,WHITE,WIDTH/2,15)
        pg.display.flip()

    def show_start_screen(self):
        def screenone(x,y):
                self.screen.blit(self.startbg,(x,y))
        screenone(0,0)
        self.draw_text("HIGH SCORE:"+str(self.highscore),70,BLUE,WIDTH/2,300)
        pg.display.flip()
        self.wait_for_key()
    def sql_data(self):
        self.root=Tk()
        self.root.title('')
        self.e=Entry(self.root,width=35)
        self.e.pack()
        def myClick():
        	self.name=self.e.get()
        	self.root.destroy()
        '''
        self.myButton=Button(self.root,text='Enter',command=myClick)
        self.myButton.pack()
        self.root.mainloop()
        mycon=mysql.connector.connect(host="localhost",user="root",password="*****",database="prog")
        cur1=mycon.cursor()
        cur1.execute("insert into Game values('{}',{})".format(self.name,self.score))
        cur1.execute("select *from Game order by Score desc")
        self.result=cur1.fetchall()
        mycon.commit()
        mycon.close()
        '''

    def show_go_screen(self):
        #self.sql_data()
        if not self.running:
            pass
        self.screen.fill(BLACK)
        def screenone(x,y):
            self.screen.blit(self.endbg,(x,y))
        screenone(0,0)
        self.draw_text("SCORE: "+str(self.score),50,WHITE,WIDTH/2,150)
        if self.score>self.highscore:
            self.highscore =self.score
            self.draw_text("NEW HIGH SCORE",100,WHITE,WIDTH/2,500)
            with open(path.join(self.dir,HS_FILE),'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("HIGH SCORE:"+str(self.highscore),70,WHITE,WIDTH/2,500)
        '''
        self.draw_text("LEADERBOARD",50,YELLOW,WIDTH/2,250)
        for i in range (0,3):
            self.draw_text(str(i+1)+')'+str(self.result[i][0])+'   '+str(self.result[i][1]),30,YELLOW,WIDTH/2,300+i*50)
        '''
        pg.display.flip()
        self.wait_for_key()
        self.wait_for_key()

    def wait_for_key(self):
        waiting=True
        while waiting:
            self.clock.tick(50)
            for event in pg.event.get():
                if event.type ==pg.QUIT:
                    waiting=False
                    self.running==False
                if event.type ==pg.KEYUP:
                    waiting =False

    def draw_text(self,text,size,color,x,y):
        font=pg.font.Font(self.font_name,size)
        text_surface=font.render(text,True,color)
        text_rect=text_surface.get_rect()
        text_rect.midtop=(x,y)
        self.screen.blit(text_surface,text_rect)
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
pg.quit()
