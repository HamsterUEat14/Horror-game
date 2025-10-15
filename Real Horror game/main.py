import pygame
from pyvidplayer import Video

pygame.init()

#setup

screen = pygame.display.set_mode((800, 600))
fps = 60
pygame.display.set_caption("Eastern Horror")
gameclock = pygame.time.Clock()

#Main menu Video
main_menu = Video('video/main_menu.mp4')
main_menu.set_size((800, 600))

#First level background
first_bg = pygame.image.load('images/bg/1st_bg.jpg').convert()
first_bg = pygame.transform.scale(first_bg, (800, 600))


#Define player action variables
moving_left = False
moving_right = False




#Entity class
class Entity(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.updatetime = pygame.time.get_ticks()
        temp_list  = []
        for i in range(1):
            img = pygame.image.load(f'images/Ent/{self.char_type}/idle/{i}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(6):
            img = pygame.image.load(f'images/Ent/{self.char_type}/walk/{i}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)    
        self.image = self.animation_list[self.action][self.frame_index]    
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    #assign movement variables when moving
    def move(self, moving_left, moving_right):
    #reset movement variables
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1    
    #update rect position // for collision detection
        self.rect.x += dx
        self.rect.y += dy

    def update_ani(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.updatetime > ANIMATION_COOLDOWN:
            self.updatetime = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out, reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.updatetime = pygame.time.get_ticks()

            


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
                

#Entity location and scale
player = Entity('player', 50 , 500, 2, 3)


 
  

#Main menu
def main_menu_loop():
    running = True
    while running:
        #draw main menu video
        main_menu.draw(screen, (0, 0))
        pygame.display.update()
        #pygame quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu.close()
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            gameclock.tick(fps)        
                    
            
            
    
def game_loop():
    global moving_left, moving_right 
    running = True
    while running:
        #background
        screen.fill((0, 0, 0))
        screen.blit(first_bg, (0, 0))
        #player
        player.update_ani()
        player.draw()
        #update player action
        if moving_left or moving_right:
            player.update_action(1) #1: walk
        else:
            player.update_action(0) #0: idle
        player.move(moving_left, moving_right)
        #pygame quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #Keypresses        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_ESCAPE:
                    running = False    
            #Key releases
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False        

        pygame.display.update()
        gameclock.tick(fps)

main_menu_loop()
game_loop()







                       
                

