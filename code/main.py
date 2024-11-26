from settings import *
from player import Player
from sprites import *
from random import randint, choice
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from json_update import *
from button import Button
import sys

class Game():
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.title = "Survivor's Eclipse"
        self.bg = pygame.image.load(r"..\images\bg2.jpg")
        self.play_mouse_pos = pygame.mouse.get_pos()
        self.pause_mouse_pos = pygame.mouse.get_pos()

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Gun Cool Down
        self.can_shoot = True
        self.gun_shoot_time = 0
        self.cooldown_duration = 100
        
        self.game_over_time = 5000
        self.collision_time = 500

        # Enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 1000)
        self.spawn_positions = []

        # audio
        self.shoot_sound = pygame.mixer.Sound(join(r"..\audio", "shoot.wav"))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join(r"..\audio", "impact.ogg"))
        self.impact_sound.set_volume(0.2)
        self.music = pygame.mixer.Sound(join(r"..\audio", "music.wav"))
        self.music_on = True  # Set music toggle as True or False
        self.music.play(loops = -1)
        self.music.set_volume(0.1)

        # Font
        self.actual_font = r"..\data\Oxanium-Bold.ttf"
        self.font = pygame.font.Font(self.actual_font, 40)
        self.font2 = pygame.font.Font(self.actual_font, 25)

        # Scores
        self.score = 0
        self.score_file = "./score_file.json"
        self.high_score = self.get_high_score()

        # Death
        self.lives = 3
        self.died = False
        self.die_time = float("inf")

        # Buttons
        self.pause_button = Button(image=None, pos=(1100, 660), text_input="PAUSE", font=self.get_font(30), base_color="White", hovering_color="Red")
        self.play_button = Button(image=None, pos=(640, 250), text_input="PLAY", font=self.get_font(55), base_color="#d7fcd4", hovering_color="white")
        self.options_button = Button(image=None, pos=(640, 400), text_input="OPTIONS", font=self.get_font(55), base_color="#d7fcd4", hovering_color="white")
        self.quit_button = Button(image=None, pos=(640, 550), text_input="QUIT GAME", font=self.get_font(55), base_color="#d7fcd4", hovering_color="white")
        self.resume_button = Button(image=None, pos=(640, 250), text_input="RESUME GAME", font=self.get_font(40), base_color="#d7fcd4", hovering_color="white")
        self.pause_quit_button = Button(image=None, pos=(640, 450), text_input="QUIT GAME", font=self.get_font(40), base_color="#d7fcd4", hovering_color="white")

        # Pause
        self.is_paused = False

                # Get the size of the background image
        bg_width, bg_height = self.bg.get_size()

        # Calculate the aspect ratio of the background
        bg_aspect_ratio = bg_width / bg_height

        # Set the target dimensions based on the window size
        if WINDOW_WIDTH / WINDOW_HEIGHT > bg_aspect_ratio:
            # The screen is wider than the background, so adjust height based on the width
            target_width = WINDOW_WIDTH
            target_height = int(WINDOW_WIDTH / bg_aspect_ratio)
        else:
            # The screen is taller than the background, so adjust width based on the height
            target_width = int(WINDOW_HEIGHT * bg_aspect_ratio)
            target_height = WINDOW_HEIGHT

        # Scale the background to the new dimensions
        self.bg_scaled = pygame.transform.scale(self.bg, (target_width, target_height))

        # Position the background: center it on the screen (if it doesn't cover it completely)
        self.bg_x = (WINDOW_WIDTH - target_width) // 2
        self.bg_y = (WINDOW_HEIGHT - target_height) // 2

        self.load_images()
        self.setup()
 
        # for i in range(6):
        #     x, y = randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)
        #     w, h = randint(60, 100), randint(50, 100)
        #     CollisionSprite((x,y), (w,h), (self.all_sprites, self.collision_sprites))

    def load_images(self):
        self.bullet_surf = pygame.image.load(join(r"..\images", "gun", "bullet.png")).convert_alpha()

        folders = list(walk(join(r"..\images","enemies")))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join(r"..\images","enemies",folder)):
                self.enemy_frames[folder] = []
                self.enemy_frames[folder].append([])
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder][0].append(surf)
                if folder == "bat":
                    self.enemy_frames[folder].append(3)
                    self.enemy_frames[folder].append(200)
                if folder == "blob":
                    self.enemy_frames[folder].append(1)
                    self.enemy_frames[folder].append(100)
                if folder == "skeleton":
                    self.enemy_frames[folder].append(2)
                    self.enemy_frames[folder].append(150)

    def input(self):
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            if self.can_shoot:
                self.shoot_sound.play()
                distance = 50
                pos = self.gun.rect.center + self.gun.player_direction * distance
                Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
                self.can_shoot = False
                self.gun_shoot_time = pygame.time.get_ticks()

    def bullet_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.gun_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(r'..\data\maps\world.tmx')

        # Order -> Create the sprites before the collision sprites to ensure they appear above the ground tiles
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name("Objects"):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        # Not in all_sprites to ensure they are not visible
        for col in map.get_layer_by_name("Collisions"):
            CollisionSprite((col.x, col.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == "Player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                # Do kill is false to have some delay before the enemy dies
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        if not sprite.killed:
                            self.score += sprite.kill_value
                            killed = True
                            sprite.destroy(killed)
                    bullet.kill()
    
    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            if self.lives >= 1:
                if self.died == False:
                    self.lives -= 1
                    self.died = True
                    self.die_time = pygame.time.get_ticks()
                else:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.die_time > self.collision_time:
                        self.died = False
                        self.die_time = float("inf")
                print(self.lives, self.died)
            else:
               self.running = False
        
    def display_score(self):
         # NTL - smoothing out the edges of a circle other than pixel 
        text_surf  = self.font2.render(f"Current Score: {self.score} | High Score: {self.high_score} | Lives: {self.lives}", True, (0,0,0))
        text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, 50))
        self.display_surface.blit(text_surf, text_rect)

    def get_high_score(self):
        create_json_file(self.score_file)
        high_score_json = read_json_file(self.score_file)
        # Safely access the "High Score" key
        high_score = high_score_json.get("High Score", 0)
        return high_score

    def run(self):
        self.reset_game()
        while self.running:
            if self.is_paused:
                self.show_pause_screen()
            else:
                pygame.display.set_caption(self.title)
                dt = self.clock.tick() / 1000
                # dt_fps = dt * self.clock.get_fps()
                # dt = 1 / int(self.clock.get_fps()) if self.clock.get_fps() > 0 else 1 / 60
                # print(dt)
                # dt_fps = dt * int(self.clock.get_fps()) if self.clock.get_fps() > 0 else 1
                self.play_mouse_pos = pygame.mouse.get_pos()  # Refresh inside the loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # self.running = False
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.pause_button.check_for_input(self.play_mouse_pos):
                            self.is_paused = True
                                
                    if event.type == self.enemy_event:
                        pos = list(choice(self.spawn_positions)) # Convert to list for mutability
                        if abs(self.player.rect.x - pos[0]) <= 300 and abs(self.player.rect.y - pos[1]) <= 300:
                            pos[0] = pos[0] * 5
                            pos[1] = pos[1] * 5
                        # print(pos, [self.player.rect.x, self.player.rect.y])
                        enemy_1 = choice(list(self.enemy_frames.values()))
                        # print(enemy_1)
                        Enemy(pos, enemy_1[0], (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, enemy_1[1], enemy_1[2])

                self.bullet_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()
                
                self.display_surface.fill("black")
                self.all_sprites.draw(self.player.rect.center)
                self.display_score()
                self.pause_button.change_color(self.play_mouse_pos)
                self.pause_button.update(self.display_surface)
            pygame.display.update()

            # print(self.bullet_sprites) # When printing a group, I get the number of sprites in that group

        if self.score > self.high_score:
            high_score_json = {
                "High Score" : self.score
            }
            write_json_file(self.score_file, high_score_json)

        # pygame.quit()
        self.game_over()
        self.main_menu()

    def reset_game(self):
        """Resets game attributes and reloads sprites."""
        self.score = 0
        self.lives = 3
        self.high_score = self.get_high_score()
        self.running = True
        self.is_paused = False
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.setup()  # Reload map, player, and initial state
    
    def get_font(self, size):
        font = pygame.font.Font(self.actual_font, size)
        return font

    def game_over(self):
    # Capture the current time to handle the game over delay
        end_time = pygame.time.get_ticks()

        # Play game-over sound effect if you have one (optional)
        # game_over_sound = pygame.mixer.Sound(join(r"..\audio", "game_over.wav"))
        # game_over_sound.play()
        
        while True:
            current_time = pygame.time.get_ticks()
            diff = current_time - end_time

            # Fill screen with black and display the background
            self.display_surface.fill("Black")
            self.display_surface.blit(self.bg_scaled, (self.bg_x, self.bg_y))

            # Display "Game Over" text
            game_over_text = self.get_font(80).render("GAME OVER", True, "#b68f40")
            game_over_rect = game_over_text.get_rect(center=(640, 100))
            self.display_surface.blit(game_over_text, game_over_rect)

            # Display player's score
            score_text = self.get_font(40).render(f"Your Score: {self.score}", True, "White")
            score_rect = score_text.get_rect(center=(640, 250))
            self.display_surface.blit(score_text, score_rect)

            # Display high score
            high_score_text = self.get_font(40).render(f"High Score: {self.high_score}", True, "White")
            high_score_rect = high_score_text.get_rect(center=(640, 350))
            self.display_surface.blit(high_score_text, high_score_rect)

            # Display prompt to return to main menu or quit
            continue_text = self.get_font(25).render("Press ENTER to Main Menu or ESC to Quit", True, "#d7fcd4")
            continue_rect = continue_text.get_rect(center=(640, 550))
            self.display_surface.blit(continue_text, continue_rect)

            pygame.display.update()

            # Check for input to either restart or quit the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.main_menu()  # Go back to the main menu
                        return  # Break out of the game over screen
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Handle the delay before returning to the main menu
            if diff >= self.game_over_time:
                break

    def options(self):
        pygame.display.set_caption("Options")
        options = True

        while options:
            self.display_surface.fill("Black")
            self.display_surface.blit(self.bg_scaled, (self.bg_x, self.bg_y))
            options_mouse_pos = pygame.mouse.get_pos()

            # Display Options title
            options_text = self.get_font(45).render("Options", True, "#b68f40")
            options_rect = options_text.get_rect(center=(640, 100))
            self.display_surface.blit(options_text, options_rect)

            # Display High Score
            high_score_text = self.get_font(35).render(f"High Score: {self.high_score}", True, "White")
            high_score_rect = high_score_text.get_rect(center=(640, 200))
            self.display_surface.blit(high_score_text, high_score_rect)

            # Display Music Toggle
            music_text = "Music: On" if self.music_on else "Music: Off"
            music_toggle = Button(image=None, pos=(640, 320), text_input=music_text, font=self.get_font(35), base_color="White", hovering_color="Red")
            music_toggle.change_color(options_mouse_pos)
            music_toggle.update(self.display_surface)

            # Back Button
            options_back = Button(image=None, pos=(640, 460), text_input="BACK", font=self.get_font(60), base_color="White", hovering_color="Red")
            options_back.change_color(options_mouse_pos)
            options_back.update(self.display_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if options_back.check_for_input(options_mouse_pos):
                        options = False
                    if music_toggle.check_for_input(options_mouse_pos):
                        # Toggle music on or off
                        self.music_on = not self.music_on
                        if self.music_on:
                            self.music.play(-1)  # Loop music
                        else:
                            self.music.stop()

            pygame.display.update()

    def show_pause_screen(self):
        pygame.display.set_caption("Pause Screen")

        # Darken and blur the screen
        dark_overlay = pygame.Surface(self.display_surface.get_size())
        dark_overlay.set_alpha(150)  # Adjust alpha to change darkness level
        dark_overlay.fill((0, 0, 0))
        self.display_surface.blit(dark_overlay, (0, 0))
        self.display_surface.blit(self.bg_scaled, (self.bg_x, self.bg_y))

        # Display "Paused" text
        pause_text = self.font.render("Paused", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(640, 100))
        self.display_surface.blit(pause_text, pause_rect)

        # Display buttons (replace with your button drawing logic)
        self.pause_mouse_pos = pygame.mouse.get_pos()  # Refresh inside the loop
        for button in [self.resume_button, self.pause_quit_button]:
            button.change_color(self.pause_mouse_pos)
            button.update(self.display_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_button.check_for_input(self.pause_mouse_pos):
                    self.is_paused = False
                if self.pause_quit_button.check_for_input(self.pause_mouse_pos):
                    self.running = False

    def main_menu(self):
        while True:
            pygame.display.set_caption("Menu")
            self.display_surface.blit(self.bg_scaled, (self.bg_x, self.bg_y))
            menu_mouse_pos = pygame.mouse.get_pos()
            menu_text = self.get_font(80).render("SURVIVOR'S ECLIPSE", True, "#b68f40")
            menu_rect = menu_text.get_rect(center = (640, 120))
            
            self.display_surface.blit(menu_text, menu_rect)

            for button in [self.play_button, self.options_button, self.quit_button]:
                button.change_color(menu_mouse_pos)
                button.update(self.display_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.check_for_input(menu_mouse_pos):
                        self.run()
                    if self.options_button.check_for_input(menu_mouse_pos):
                        self.options()
                    if self.quit_button.check_for_input(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.main_menu()


# Add a health mechanic
    