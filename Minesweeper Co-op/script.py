import pygame, sys
from button import Button

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Minesweeper Co-op')

BG = pygame.image.load('assets/Background.png')

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

def play():
    while True:
        play_mouse_pos = pygame.mouse.get_pos()

        screen.fill("black")

        play_text = get_font(32).render("This is the game screen", True, (100, 0, 0))
        play_rect = play_text.get_rect(center=(640,260))
        screen.blit(play_text, play_rect)

        play_back = Button(image=None, pos=(640, 460),
                            text_input="Back", font=get_font(32), base_color="White", hovering_color="green")

        play_back.changecolor(play_mouse_pos)
        play_back.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_back.checkforinput(play_mouse_pos):
                    main_menu()

        pygame.display.update()

def options():
    while True:
        options_mouse_pos = pygame.mouse.get_pos()

        screen.fill("white")
        options_text = get_font(32).render("This is the options screen", True, (0, 0, 0))
        options_rect = options_text.get_rect(center=(640,260))
        screen.blit(options_text, options_rect)

        options_back = Button(image=None, pos=(640, 460),
                              text_input="Back", font=get_font(32), base_color="black", hovering_color="green")

        options_back.changecolor(options_mouse_pos)
        options_back.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if options_back.checkforinput(options_mouse_pos):
                    main_menu()

        pygame.display.update()

def main_menu():
    pygame.display.set_caption('Minesweeper Co-op Menu')

    while True:
        screen.blit(BG, (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("Main Menu", True, (255, 255, 100))
        menu_rect = menu_text.get_rect(center = (640, 100))

        play_button = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
                            text_input="PLAY", font=get_font(100), base_color="#d7fcd4", hovering_color="white")
        options_button = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
                                text_input="OPTIONS", font=get_font(100), base_color="#d7fcd4", hovering_color="white")
        quit_button = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
                                 text_input="QUIT", font=get_font(100), base_color="#d7fcd4", hovering_color="white")

        screen.blit(menu_text, menu_rect)

        for button in [play_button, options_button, quit_button]:
            button.changecolor(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkforinput(menu_mouse_pos):
                    play()
                if options_button.checkforinput(menu_mouse_pos):
                    options()
                if quit_button.checkforinput(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()