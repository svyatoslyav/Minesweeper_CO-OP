import pygame
import random
pygame.init()

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

bg_color = (192, 192, 192)
grid_color = (128, 128, 128)

game_width = 10  # Change this to increase size
game_height = 10  # Change this to increase size
numMine = 9  # Number of mines
grid_size = 32  # Size of grid (WARNING: make sure to change the images dimension as well)
border = 16  # Top border
top_border = 100  # Left, Right, Bottom border
display_width = grid_size * game_width + border * 2  # Display width
display_height = grid_size * game_height + border + top_border  # Display height
gameDisplay = pygame.display.set_mode((display_width, display_height))  # Create display
timer = pygame.time.Clock()  # Create timer
pygame.display.set_caption("Minesweeper")  # Set the caption of window

# Import files
spr_emptyGrid = pygame.image.load("Sprites/empty.png")
spr_flag = pygame.image.load("Sprites/flag.png")
spr_grid = pygame.image.load("Sprites/Grid.png")
spr_grid1 = pygame.image.load("Sprites/grid1.png")
spr_grid2 = pygame.image.load("Sprites/grid2.png")
spr_grid3 = pygame.image.load("Sprites/grid3.png")
spr_grid4 = pygame.image.load("Sprites/grid4.png")
spr_grid5 = pygame.image.load("Sprites/grid5.png")
spr_grid6 = pygame.image.load("Sprites/grid6.png")
spr_grid7 = pygame.image.load("Sprites/grid7.png")
spr_grid8 = pygame.image.load("Sprites/grid8.png")
spr_mine = pygame.image.load("Sprites/mine.png")
spr_mineClicked = pygame.image.load("Sprites/mineClicked.png")
spr_mineFalse = pygame.image.load("Sprites/mineFalse.png")


# Create global values
grid = []  # The main grid
mines = []  # Pos of the mines


# Create function to draw texts
def draw_text(txt, s, y_off=0):
    screen_text = pygame.font.SysFont("Calibre", s, True).render(txt, True, (0, 0, 0))
    rect = screen_text.get_rect()
    rect.center = (int(game_width * grid_size / 2 + border), int(game_height * grid_size / 2 + top_border + y_off))
    gameDisplay.blit(screen_text, rect)


# Create class grid
class Grid:
    def __init__(self, x_grid, y_grid, type):
        self.xGrid = x_grid  # X pos of grid
        self.yGrid = y_grid  # Y pos of grid
        self.clicked = False  # Boolean var to check if the grid has been clicked
        self.mineClicked = False  # Bool var to check if the grid is clicked and it's a mine
        self.mineFalse = False  # Bool var to check if the player flagged the wrong grid
        self.flag = False  # Bool var to check if player flagged the grid
        # Create rectObject to handle drawing and collisions
        self.rect = pygame.Rect(border + self.xGrid * grid_size, top_border + self.yGrid * grid_size, grid_size, grid_size)
        self.val = type  # Value of the grid, -1 is mine

    def draw_grid(self):
        # Draw the grid according to bool variables and value of grid
        if self.mineFalse:
            gameDisplay.blit(spr_mineFalse, self.rect)
        else:
            if self.clicked:
                if self.val == -1:
                    if self.mineClicked:
                        gameDisplay.blit(spr_mineClicked, self.rect)
                    else:
                        gameDisplay.blit(spr_mine, self.rect)
                else:
                    if self.val == 0:
                        gameDisplay.blit(spr_emptyGrid, self.rect)
                    elif self.val == 1:
                        gameDisplay.blit(spr_grid1, self.rect)
                    elif self.val == 2:
                        gameDisplay.blit(spr_grid2, self.rect)
                    elif self.val == 3:
                        gameDisplay.blit(spr_grid3, self.rect)
                    elif self.val == 4:
                        gameDisplay.blit(spr_grid4, self.rect)
                    elif self.val == 5:
                        gameDisplay.blit(spr_grid5, self.rect)
                    elif self.val == 6:
                        gameDisplay.blit(spr_grid6, self.rect)
                    elif self.val == 7:
                        gameDisplay.blit(spr_grid7, self.rect)
                    elif self.val == 8:
                        gameDisplay.blit(spr_grid8, self.rect)

            else:
                if self.flag:
                    gameDisplay.blit(spr_flag, self.rect)
                else:
                    gameDisplay.blit(spr_grid, self.rect)

    def revealGrid(self):
        self.clicked = True
        # Auto reveal if it's a 0
        if self.val == 0:
            for x in range(-1, 2):
                if 0 <= self.xGrid + x < game_width:
                    for y in range(-1, 2):
                        if 0 <= self.yGrid + y < game_height:
                            if not grid[self.yGrid + y][self.xGrid + x].clicked:
                                grid[self.yGrid + y][self.xGrid + x].revealGrid()
        elif self.val == -1:
            # Auto reveal all mines if it's a mine
            for m in mines:
                if not grid[m[1]][m[0]].clicked:
                    grid[m[1]][m[0]].revealGrid()

    def update_value(self):
        # Update the value when all grid is generated
        if self.val != -1:
            for x in range(-1, 2):
                if 0 <= self.xGrid + x < game_width:
                    for y in range(-1, 2):
                        if 0 <= self.yGrid + y < game_height:
                            if grid[self.yGrid + y][self.xGrid + x].val == -1:
                                self.val += 1


def game_loop():
    game_state = "Playing"  # Game state
    mine_left = numMine  # Number of mine left
    global grid  # Access global var
    grid = []
    global mines
    t = 0  # Set time to 0

    # Generating mines
    mines = [[random.randrange(0, game_width),
              random.randrange(0, game_height)]]

    for c in range(numMine - 1):
        pos = [random.randrange(0, game_width),
               random.randrange(0, game_height)]
        same = True
        while same:
            for i in range(len(mines)):
                if pos == mines[i]:
                    pos = [random.randrange(0, game_width), random.randrange(0, game_height)]
                    break
                if i == len(mines) - 1:
                    same = False
        mines.append(pos)

    # Generating entire grid
    for j in range(game_height):
        line = []
        for i in range(game_width):
            if [i, j] in mines:
                line.append(Grid(i, j, -1))
            else:
                line.append(Grid(i, j, 0))
        grid.append(line)

    # Update of the grid
    for i in grid:
        for j in i:
            j.update_value()

    # Main Loop
    while game_state != "Exit":
        # Reset screen
        gameDisplay.fill(bg_color)

        # User inputs
        for event in pygame.event.get():
            # Check if player close window
            if event.type == pygame.QUIT:
                game_state = "Exit"

            # Check if play restart
            if game_state == "Game Over" or game_state == "Win":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_state = "Exit"
                        game_loop()
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    for i in grid:
                        for j in i:
                            if j.rect.collidepoint(event.pos):
                                if event.button == 1:
                                    # If player left-clicked of the grid
                                    j.revealGrid()
                                    # Toggle flag off
                                    if j.flag:
                                        mine_left += 1
                                        j.flag = False
                                    # If it's a mine
                                    if j.val == -1:
                                        game_state = "Game Over"
                                        j.mineClicked = True
                                elif event.button == 3:
                                    # If the player right-clicked
                                    if not j.clicked:
                                        if j.flag:
                                            j.flag = False
                                            mine_left += 1
                                        else:
                                            j.flag = True
                                            mine_left -= 1


        # Check if won
        w = True
        for i in grid:
            for j in i:
                j.draw_grid()
                if j.val != -1 and not j.clicked:
                    w = False
        if w and game_state != "Exit":
            game_state = "Win"

        # Draw Texts
        if game_state != "Game Over" and game_state != "Win":
            t += 1
        elif game_state == "Game Over":
            draw_text("Game Over!", 50, )
            draw_text("R to restart", 35, 50)
            for i in grid:
                for j in i:
                    if j.flag and j.val != -1:
                        j.mineFalse = True
        else:
            draw_text("You WON!", 50)
            draw_text("R to restart", 35, 50)

        # Draw time
        s = str(t // 15)
        screen_text = pygame.font.SysFont("Calibre", 50).render(s, True, (0, 0, 0))
        gameDisplay.blit(screen_text, (border, border))
        # Draw mine left
        screen_text = pygame.font.SysFont("Calibre", 50).render(mine_left.__str__(), True, (0, 0, 0))
        gameDisplay.blit(screen_text, (display_width - border - 50, border))

        pygame.display.update()  # Update screen

        timer.tick(15)  # Tick fps
