from settings import *
from math import atan2, degrees

# class CollisionSprite(pygame.sprite.Sprite):
#     def __init__(self, pos, size, groups):
#         super().__init__(groups)
#         self.image = pygame.Surface(size)
#         self.image.fill('blue')
#         self.rect = self.image.get_frect(center = pos)

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # Connect with player
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(1,0)

        # Sprite setup
        super().__init__(groups)
        self.groups = groups
        self.gun_surf = pygame.image.load(join("..\images", "gun", "gun.png")).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        # self.player.rect.center -> Won't work as there are times that the player center can be off the screen because of the camera
        # Since the player is always at the center of the screen, just get the center position
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()
        # print(mouse_pos, player_pos, self.player_direction)
    
    def rotate_gun(self):
        # Given x and y, I get the angle btn the hypotenuse and x in radians, convert to degrees
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            # The angle of the gun is -ve, convert to +ve via absolute
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True) # Horizontally, Vertically

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.direction = direction
        self.speed = 1000
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 500

    def move(self, dt):
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt):
        self.move(dt)

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, kill_value, speed):
        super().__init__(groups)
        self.player = player

        # image
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = speed

        self.death_time = 0
        self.death_duration = 300

        self.killed = False

        self.kill_value = kill_value

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        # update rect position + collision
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision = "horizontal"
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision = "vertical"

        self.rect.center = self.hitbox_rect.center

    # Instead of copy pasting from Player, create a class that Enemy and Player can inherit from
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    # Moving right
                    if self.player_direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    # Moving left
                    if self.player_direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    # Moving up
                    if self.player_direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    # Moving down
                    if self.player_direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

    def destroy(self, killed):
        # Start a timer
        self.death_time = pygame.time.get_ticks()

        # Change the enemy to its black and white mask - silhouette
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()

        # Remove black pixels from the surf
        surf.set_colorkey('black')
        self.image = surf

        self.killed = killed

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()