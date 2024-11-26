import pygame, sys
from button import Button
from settings import *
from main import Game

pygame.init()
game = Game()
SCREEN = game.display_surface
pygame.display.set_caption("Vampire Survivor")

bg = pygame.image.load(r"..\images\bg.jpg")

def get_font(size):
    font = pygame.font.Font(game.actual_font, size)
    return font

    def play(self): 
        play_mouse_pos = pygame.mouse.get_pos()
        pygame.display.set_caption("Play")
        self.running = True
        self.run()

        play_back = Button(image=None, pos=(1100, 660), text_input="BACK", font=self.get_font(25), base_color="White", hovering_color="Red")

        play_back.change_color(play_mouse_pos)
        play_back.update(self.display_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            

        pygame.display.update()
def play(): 
    play_mouse_pos = pygame.mouse.get_pos()
    pygame.display.set_caption("Play")
    Game.run()

    play_back = Button(image=None, pos=(1100, 660), text_input="BACK", font=get_font(25), base_color="White", hovering_color="Red")

    play_back.change_color(play_mouse_pos)
    play_back.update(SCREEN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if play_back.check_for_input(play_mouse_pos):
                main_menu()

    pygame.display.update()

def options():
    options_mouse_pos = pygame.mouse.get_pos()
    pygame.display.set_caption("Options")
    SCREEN.fill("white")

    options_text = get_font(45).render("Options screen", True, "Black")
    options_rect = options_text.get_rect(center=(640, 260))
    SCREEN.blit(options_text, options_rect)

    options_back = Button(image=None, pos=(640,460), text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Red")
    
    options_back.change_color(options_mouse_pos)
    options_back.update(SCREEN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if options_back.check_for_input(options_mouse_pos):
                main_menu()

    pygame.display.update()

def main_menu():
    pygame.display.set_caption("Menu")

    while True:
        SCREEN.blit(bg, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()
        menu_text = get_font(100).render("MAIN MENU", True, "#b68f40")
        menu_rect = menu_text.get_rect(center = (640, 100))
        button_font = pygame.font.Font(None, 36)  # Use default font, or specify a font file
        play_button = Button(image=None, pos=(640, 250), text_input="PLAY", font=get_font(75), base_color="#d7fcs4", hovering_color="white")
        options_button = Button(image=None, pos=(640, 400), text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="white")
        quit_button = Button(image=None, pos=(640, 550), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="white")
        
        SCREEN.blit(menu_text, menu_rect)

        for button in [play_button, options_button, quit_button]:
            button.change_color(menu_mouse_pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(menu_mouse_pos):
                    play()
                if options_button.check_for_input(menu_mouse_pos):
                    options()
                if quit_button.check_for_input(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

if __name__ == '__main__':
    main_menu()