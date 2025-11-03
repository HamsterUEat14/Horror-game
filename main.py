import pygame
import os
import random
from pyvidplayer import Video
from typing import cast

pygame.init()

#setup
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
fps = 60
pygame.display.set_caption("Eastern Horror")
gameclock = pygame.time.Clock()

#Main menu Video
main_menu = Video('video/main_menu.mp4')
main_menu.set_size((SCREEN_WIDTH, SCREEN_HEIGHT))

#First level background
first_bg = pygame.image.load('images/bg/1st_bg.jpg').convert()
first_bg = pygame.transform.scale(first_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
Floor = (34, 34, 34)

#game variables
GRAVITY = 0.75
TILE_SIZE = 50

#colors
RED = (139, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


#Define player action variables
moving_left = False
moving_right = False
attack = False

#attack effects
attack_effect = pygame.image.load('images/icons/meleeatk.png').convert_alpha()
attack_effect = pygame.transform.scale(attack_effect, (100, 100))

#items
health_stone = pygame.image.load('images/icons/health_stone.png').convert_alpha()
health_stone =  pygame.transform.scale(health_stone, (50, 50))
speed_boost = pygame.image.load('images/icons/speed_boost.png').convert_alpha()
speed_boost = pygame.transform.scale(speed_boost, (50, 50))
item_boxes = {
    'Health'    : health_stone,
    'Speed'     : speed_boost
}

#define font
font = pygame.font.SysFont('Bauhaus 93', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Entity class
class Entity(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.is_alive = True
        self.char_type = char_type
        self.health = 100
        self.hp = self.health
        self.max_health = self.health
        self.speed = speed
        self.base_speed = speed
        self.boosted_speed = speed + 3
        self.speed_boost_active = False
        self.speed_boost_start_time = 0
        self.attack_cooldown = 0
        self.direction = 1
        self.y_vel = 0
        self.in_air = True
        self.jump = False
        self.flip = False
        self.atk = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.updatetime = pygame.time.get_ticks()

        #ai variables
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0



        #load all images for the players
        animation_types = ['idle', 'walk', 'jump', 'heavy', 'death', 'hit']
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

    def update(self):
        self.update_ani()
        self.check_alive()
        #update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
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
        if self.rect.bottom + dy > 1000:
            dy = 1000 - self.rect.bottom
            self.in_air = False    

        #update rect position // for collision detection
        self.rect.x += dx
        self.rect.y += dy

    def attack(self):
        if self.attack_cooldown == 0:
            self.attack_cooldown = 20
            # spawn effect outside the player's rect so it doesn't immediately collide with owner
            spawn_x = int(self.rect.centerx + (self.rect.width / 2 + attack_effect.get_width() / 2) * self.direction)
            effect = Attack(spawn_x, self.rect.centery, self.direction, self)
            attack_group.add(effect)
            if effect.direction == -1:
                effect.image = pygame.transform.flip(effect.image, True, False)

    def ai(self):
        # simple patrol: move right when direction == 1, left when -1
        if not (self.is_alive and player.is_alive):
            return
        if self.idling == False and random.randint(1, 200) == 1:
            self.update_action(0)  # idle
            self.idling = True
            self.idling_counter = 50
        if self.idling == False:
            if self.direction == 1:
                # move(left=False, right=True)
                self.move(False, True)
            else:
                # move(left=True, right=False)
                self.move(True, False)
            self.update_action(1)  # walk        
            self.move_counter += 1
            # after TILE_SIZE frames flip direction and reset counter
            if self.move_counter >= TILE_SIZE:
                self.direction *= -1
                self.move_counter = 0 
        else:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False               

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
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.updatetime = pygame.time.get_ticks()
       
        
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.is_alive = False
            self.update_action(4) # death

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
             

            
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Speed':
                # store base speed once, apply boost and set start time/active flag
                player.base_speed = getattr(player, 'base_speed', player.speed)
                player.speed = player.boosted_speed
                player.speed_boost_start_time = pygame.time.get_ticks()
                player.speed_boost_active = True
            self.kill()
            
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Attack(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.speed = 20
        self.image = attack_effect
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.owner = owner  # owner entity to avoid hitting self

    def update(self):
        # move attack effect
        self.rect.x += (self.direction * self.speed)

        # remove if off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            return

        # check collision with targets, skip owner
        for target in (player, enemy_group):
            if target is self.owner:
                continue
            if player.is_alive and self.rect.colliderect(player.rect):
                player.health -= 10
                self.kill()
            for enemy in enemy_group:
                if enemy.is_alive and self.rect.colliderect(enemy.rect):
                    enemy.health -= 40
                    self.kill()
                
                   

#Create Group
enemy_group = pygame.sprite.Group()
attack_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

#temp
item_box = ItemBox('Health', 1000, 930)
item_box_group.add(item_box)
item_box = ItemBox('Speed', 800, 930)
item_box_group.add(item_box)


# Entity location and scale
player = Entity('player', 100, 900, 4, 6)
health_bar = HealthBar(10, 10, player.health, player.max_health)

enemy = Entity('enemy', 200, 900, 4, 5)
enemy_group.add(enemy)
enemy2 = Entity('enemy', 400, 900, 4, 5)
enemy_group.add(enemy2)

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
    pygame.draw.line(screen, Floor, (0, 980), (1920, 980), 120)

    #update player action
    if player.is_alive:
        if attack:
            player.attack()
        if player.atk:
            player.update_action(3)  # heavy attack
        elif player.in_air:
            player.update_action(2)  # jump
        elif moving_left or moving_right:
            player.update_action(1)  # walk
        else:
            player.update_action(0)  # idle

    # then update animation and draw
    #player update and draw
    player.update()
    player.draw()


    #enemy update and draw
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()
        
    #group updates and draws
    attack_group.update()
    attack_group.draw(screen)
    item_box_group.update()
    item_box_group.draw(screen)

    # restore speed boost when duration elapsed
    now = pygame.time.get_ticks()
    if getattr(player, 'speed_boost_active', False):
        start = getattr(player, 'speed_boost_start_time', 0)
        duration = getattr(player, 'speed_boost_duration', 5000)
        if now - start >= duration:
            player.speed_boost_active = False
            player.speed = getattr(player, 'base_speed', player.speed)
            # optional: delattr base_speed/speed_boost_start_time if you want to clean up

    #text draw
    health_bar.draw(player.health)
    if player.speed_boost_active:
        screen.blit(speed_boost, (10, 40))
    
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
            if event.key == pygame.K_SPACE:
                player.atk = True
                attack = True
     #reset inputs           
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                player.atk = False
                attack = False
                       
           

    pygame.display.update()
    gameclock.tick(fps)

pygame.quit()















