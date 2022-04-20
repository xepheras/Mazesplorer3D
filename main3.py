###3D Development (WALLS EDITION)
##
## Luna Chapman
##

#import necessary libraries
import pygame #graphics :D
import numpy as np #nummbers :D
from config import * #my file with some numbers in a place i can easily adjust
from numba import njit #compiler, makes code run about 10 times faster. very useful

#set some graphhics
sky = pygame.image.load('background.png')
sky = pygame.surfarray.array3d(pygame.transform.scale(sky, (360, halfvres*2)))
floor = pygame.surfarray.array3d(pygame.image.load('floor.png'))/255
wall = pygame.surfarray.array3d(pygame.image.load('wall.png'))/255
ceiling = pygame.surfarray.array3d(pygame.image.load('ceiling.png'))/255


#the game
class Game:
    #run at launch
    def __init__(self):
        #initialise pygame
        pygame.init()
        #set a bunch of variables used later
        self.screen = pygame.display.set_mode((screenh,screenv)) #window
        self.running = True #game open/closed
        self.playing = True #player dead/alive
        self.clock = pygame.time.Clock() 
        self.posx, self.posy, self.rot = 0, 0, 0 #location and direction
        self.map1 = np.random.choice([0,0,0,1], (size,size))
        self.frame = np.random.uniform(0,1, (hres, halfvres*2, 3)) #screen innit
        pygame.mouse.set_visible(False) #makes mouse invisible on window
    
        
    #creates graphiczs
    def draw(self):

        #this function does all the important stuff
        self.frame = nextframe(self.posx, self.posy, self.rot, self.frame, sky, floor, hres, halfvres, mod, self.map1, size, wall, ceiling)

        #creates the floor. quite snazzy
        surf = pygame.surfarray.make_surface(self.frame*255)
        surf = pygame.transform.scale(surf, (screenh, screenv))

        #sets title of window (currently fps so i could optimise)
        fps = int(self.clock.get_fps())
        pygame.display.set_caption("FPS: " + str(fps))

        #updates the screen
        self.screen.blit(surf, (0,0))
        pygame.display.update()
        
        #runs 'movement' function
        self.posx, self.posy, self.rot = self.movement(self.posx,self.posy,self.rot,pygame.key.get_pressed(), self.clock.tick())
        #keeps mouse centered
        pygame.mouse.set_pos([400,300])

        
    #moving
    def movement(self,posx,posy,rot,keys, et):

        
        #horizontal mouse movement controls direction you face
        p_mouse = pygame.mouse.get_pos()
        rot = rot - 4*np.pi*(0.5-(p_mouse[0]-400)/6400)
                            

        #all the movements and that
        if keys[pygame.K_LEFT] or keys[ord('a')]:
             posx, posy = posx + np.sin(rot)*0.005*et, posy - np.cos(rot)*0.005*et
        elif keys[pygame.K_RIGHT] or keys[ord('d')]:
            posx, posy = posx - np.sin(rot)*0.005*et, posy + np.cos(rot)*0.005*et
        elif keys[pygame.K_UP] or keys[ord('w')]:
            posx, posy = posx + np.cos(rot)*0.005*et, posy + np.sin(rot)*0.005*et
        elif keys[pygame.K_DOWN] or keys[ord('s')]:
            posx, posy = posx - np.cos(rot)*0.005*et, posy - np.sin(rot)*0.005*et
        return posx, posy, rot
        
    #its meant to close the game but?
    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    #everything to be ran. nice and simple
    def main(self):
        while self.playing:
            self.clock.tick(60)
            self.event()
            self.draw()
            
        self.running = False

#speeds up function somehow (very nice)
        #the downside is i need to seperate chunks of the code into functions.
        #it doesnt work with classes but id rather make this compromise than heavily complicate things and get less performance still
@njit()
#draws frame
def nextframe(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, map1, size, wall,ceiling):
    #each value of x
    for i in range(hres):

            #direction for floor positions
            rot_i = rot + np.deg2rad(i/mod-30)
            #fancy math functions
            sin,cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod-30))
            #skie
            frame[i][:] = sky[int(np.rad2deg(rot_i)%359)][:]
            
            x, y = posx, posy
            while map1[int(x)%(size-1)][int(y)%(size-1)] == 0:
                x, y = x+0.02*cos, y + 0.02*sin

            n = abs((x - posx)/cos)
            
            h = int(halfvres/(n*cos2 + 0.001))

            xx = int(x*2%1*99)
            
            if x%1 <0.02 or x%1 > 0.98:
                 xx = int(y*3%1*99)
            yy = np.linspace(0, 198, h*2)%99

            shade = 0.3 + 0.7*(h/halfvres)

            if shade > 1:
                shade = 1

            
            for k in range(h*2):
                if halfvres - h+k >= 0 and halfvres - h+k <= 2*halfvres:
                    frame[i][halfvres - h+k] = shade*wall[xx][int(yy[k])]
                    if halfvres+3*h-k < halfvres*2:
                        frame[i][halfvres+3*h-k] = shade*wall[xx][int(yy[k])]
                if halfvres - h+k <= 0 and halfvres - h+k >= 2*halfvres:
                    frame[i][halfvres - h+k] = shade*wall[xx][int(yy[k])]
                    if halfvres+3*h-k < halfvres*2:
                        frame[i][halfvres+3*h-k] = shade*wall[xx][int(yy[k])]
                

            #each value of y in this column of x
            for j in range (halfvres -h):
                #draws ground, in the bottom half of the screen
                n = (halfvres/(halfvres-j)) / cos2
                x, y = posx + cos*n, posy + sin*n
                xx, yy = int(x*2%1*100), int(y*2%1*100)

                shade = 0.2 + 0.8*(1-j/halfvres)

                #if int(x)%2 == int(y)%2:
                #    frame[i][j] = [0,0,0]
                #else:
                #    frame[i][j] = [1,1,1]
                    
                
                frame[i][halfvres*2-j-1] = (2*shade*floor[xx][yy] + frame[i][halfvres*2-j-1])/3
                frame[i][j] = (shade*ceiling[xx][yy]+frame[i][j])/3
                
    return frame
    
#runs the game
g = Game()
while g.running:
    g.main()
    
#should ideally close it but it doesnt, i give up
pygame.quit()
sys.exit()
