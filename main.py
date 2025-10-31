import pygame
import os
from pyvidplayer import Video

pygame.init()

#setup

screen = pygame.display.set_mode((1920, 1080))
fps = 60
pygame.display.set_caption("Eastern Horror")
gameclock = pygame.time.Clock()

#Main menu Video
main_menu = Video('video/main_menu.mp4')
main_menu.set_size((1920, 1080))

#First level background
first_bg = pygame.image.load('images/bg/1st_bg.jpg').convert()
first_bg = pygame.transform.scale(first_bg, (1920, 1080))
Floor = (0, 0, 0)

#game variables
GRAVITY = 0.75
#Define player action variables
moving_left = False
moving_right = False




#Entity class
class Entity(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.is_alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.y_vel = 0
        self.in_air = True
        self.jump = False
        self.flip = False
        self.light_attack = False
        self.heavy_attack = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.updatetime = pygame.time.get_ticks()
        #load all images for the players
        animation_types = ['idle', 'walk', 'jump', 'light', 'heavy']
        for animation in animation_types:
            #reset temporary list of images
            temp_list  = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'images/Ent/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/Ent/{self.char_type}/{animation}/{i}.png').convert_alpha()
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
        if self.jump == True and self.in_air == False:
            self.y_vel = -17
            self.jump = False
            self.in_air = True
    #gravity
        self.y_vel += GRAVITY
        if self.y_vel > 10:
            self.y_vel = 10
        dy += self.y_vel
    #check collision with floor
        if  self.rect.bottom + dy > 1000:
         dy = 1000 - self.rect.bottom
         self.in_air = False    
                
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
                
# Entity location and scale
player = Entity('player', 50, 900, 4, 5)

# Main menu loop
running = True
while running:
    # draw main menu video
    main_menu.draw(screen, (0, 0))
    pygame.display.update()
    # pygame quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            main_menu.close()
        if event.type == pygame.MOUSEBUTTONDOWN:
            running = False
            main_menu.close()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                main_menu.close()
        gameclock.tick(fps)
        

                           
    
#game loop 
running = True
while running:
    #background
    screen.fill((0, 0, 0))
    screen.blit(first_bg, (0, 0))
    pygame.draw.line(screen, Floor, (0, 1030), (1920, 980), 170)

    #update player action
    if player.is_alive:
        if player.heavy_attack:
            player.update_action(4)  # heavy attack
        elif player.light_attack:
            player.update_action(3)  # light attack
        elif player.in_air:
            player.update_action(2)  # jump
        elif moving_left or moving_right:
            player.update_action(1)  # walk
        else:
            player.update_action(0)  # idle

    # then update animation and draw
    player.update_ani()
    player.draw()

    # move regardless (or only if alive, as you prefer)
    if player.is_alive:
        player.move(moving_left, moving_right)

    # input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.is_alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_x:
                player.light_attack = True
            if event.key == pygame.K_c:
                player.heavy_attack = True
     #reset inputs           
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_x:
                player.light_attack = False
            if event.key == pygame.K_c:
                player.heavy_attack = False
                       
           

    pygame.display.update()
    gameclock.tick(fps)

pygame.quit()













