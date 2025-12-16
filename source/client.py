import pyperclip
import pygame
import socket
import pickle
import threading
import os
import time
import server
import ctypes
import sys

# 2. Створюємо унікальний ID для програми
# Можна написати будь-що, головне щоб рядок був унікальним
myappid = 'minesweeper.coop.game'

# 3. Кажемо Windows використовувати цей ID
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

# --- КОНСТАНТИ ---
PORT = 5555
CELL_SIZE = 32
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_VICTORY = 3

# Глобальні змінні
client = None
game_grid = []
visible_grid = []
game_state = STATE_MENU
running = True
sprites = {}
GRID_WIDTH = 10
GRID_HEIGHT = 10
# Розмір вікна для меню зробимо більшим, щоб все влізло
WIDTH, HEIGHT = 500, 500

pygame.init()

try:
    icon_path = os.path.join("Sprites", "icon.png")
    if os.path.exists(icon_path):
        program_icon = pygame.image.load(icon_path)
        pygame.display.set_icon(program_icon)
except Exception as e:
    print(f"Icon error: {e}")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кооперативний Сапер")

try:
    # Для вікна Pygame краще використовувати .png
    program_icon = pygame.image.load(os.path.join("Sprites", "icon.png"))
    pygame.display.set_icon(program_icon)
except Exception as e:
    print(f"Не вдалося завантажити іконку: {e}")

font_ui = pygame.font.SysFont('Arial', 20)
font_large = pygame.font.SysFont('Arial', 32, bold=True)
font_small = pygame.font.SysFont('Arial', 16)


# --- КЛАС ДЛЯ ПОЛІВ ВВЕДЕННЯ ---
class TextInput:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = pygame.Color('dodgerblue2')
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color = self.color_inactive
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        # Малюємо текст
        txt_surface = font_ui.render(self.text, True, self.color)
        # Розширюємо поле, якщо текст довгий
        width = max(self.rect.w, txt_surface.get_width() + 10)
        self.rect.w = width
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_val(self):
        try:
            return int(self.text)
        except:
            return 0


# --- ФУНКЦІЇ ---

def load_sprites():
    def load(name):
        path = os.path.join("Sprites", name)
        try:
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except:
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
            surf.fill((100, 100, 100))
            return surf

    sprites['unknown'] = load("Grid.png")
    sprites['empty'] = load("empty.png")
    sprites['flag'] = load("flag.png")
    sprites['mine'] = load("mine.png")
    sprites['mine_clicked'] = load("mineClicked.png")
    for i in range(1, 9):
        sprites[i] = load(f"grid{i}.png")


def receive_data():
    global game_grid, visible_grid, game_state, running
    while running:
        try:
            data = client.recv(4096 * 16)  # Ще більший буфер для великих карт
            if not data: break
            game_grid, visible_grid, game_state = pickle.loads(data)
        except:
            break
    print("Відключено від сервера")


def start_hosting(w, h, m):
    """Запускає сервер з параметрами"""
    # Передаємо параметри у start_server
    server_thread = threading.Thread(target=server.start_server, args=(w, h, m))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)


def try_connect(ip):
    global client, GRID_WIDTH, GRID_HEIGHT, WIDTH, HEIGHT
    try:
        temp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_client.settimeout(3)
        temp_client.connect((ip, PORT))
        temp_client.settimeout(None)

        config_data = temp_client.recv(4096)
        config = pickle.loads(config_data)

        GRID_WIDTH = config['w']
        GRID_HEIGHT = config['h']
        WIDTH = GRID_WIDTH * CELL_SIZE
        HEIGHT = GRID_HEIGHT * CELL_SIZE

        return temp_client
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def connection_menu():
    clock = pygame.time.Clock()
    error_msg = ""

    # Створюємо поля введення
    ip_input = TextInput(200, 80, 200, 32, '')

    # Поля для налаштувань сервера
    w_input = TextInput(200, 270, 60, 32, '20')
    h_input = TextInput(280, 270, 60, 32, '15')
    m_input = TextInput(360, 270, 60, 32, '40')

    inputs = [ip_input, w_input, h_input, m_input]

    host_btn = pygame.Rect(50, 320, 400, 50)
    join_btn = pygame.Rect(50, 130, 400, 40)

    while True:
        screen.fill((30, 30, 30))

        # --- JOIN SECTION ---
        title = font_large.render("Minesweeper CO-OP", True, (255, 255, 255))
        screen.blit(title, (100, 20))

        screen.blit(font_ui.render("Server IP:", True, (200, 200, 200)), (50, 85))
        ip_input.draw(screen)

        # Кнопка Join
        pygame.draw.rect(screen, (0, 100, 200), join_btn)
        j_txt = font_ui.render("JOIN GAME", True, (255, 255, 255))
        screen.blit(j_txt, j_txt.get_rect(center=join_btn.center))

        # Розділювач
        pygame.draw.line(screen, (100, 100, 100), (30, 200), (470, 200), 1)

        # --- HOST SECTION ---
        screen.blit(font_large.render("Create New Game", True, (0, 255, 100)), (130, 210))

        screen.blit(font_small.render("W", True, (200, 200, 200)), (210, 250))
        screen.blit(font_small.render("H", True, (200, 200, 200)), (290, 250))
        screen.blit(font_small.render("Mines", True, (200, 200, 200)), (360, 250))

        screen.blit(font_ui.render("Settings:", True, (200, 200, 200)), (50, 275))

        w_input.draw(screen)
        h_input.draw(screen)
        m_input.draw(screen)

        # Кнопка Host
        pygame.draw.rect(screen, (0, 150, 0), host_btn)
        h_txt = font_ui.render("HOST & START", True, (255, 255, 255))
        screen.blit(h_txt, h_txt.get_rect(center=host_btn.center))

        info_msg = font_small.render("При створенні гри ваш IP скопіюється автоматично", True, (150, 150, 150))
        screen.blit(info_msg, info_msg.get_rect(center=(host_btn.centerx, host_btn.bottom + 20)))

        if error_msg:
            err = font_small.render(error_msg, True, (255, 100, 100))
            screen.blit(err, (50, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            # Обробка введення тексту
            for inp in inputs:
                inp.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # JOIN
                if join_btn.collidepoint(event.pos):
                    res = try_connect(ip_input.text)
                    if res:
                        return res
                    else:
                        error_msg = "Cannot connect to server"

                # HOST
                if host_btn.collidepoint(event.pos):
                    # Валідація
                    w = w_input.get_val()
                    h = h_input.get_val()
                    m = m_input.get_val()

                    if w < 5 or h < 5:
                        error_msg = "Too small! Min 5x5"
                    elif w > 50 or h > 40:
                        error_msg = "Too big! Max 50x40"
                    elif m >= w * h:
                        error_msg = "Too many mines!"
                    else:

                        try:
                            my_ip = socket.gethostbyname(socket.gethostname())
                            pyperclip.copy(my_ip)
                            print(f"IP {my_ip} copied!")
                        except Exception as e:
                            print(f"Error copying IP: {e}")

                        start_hosting(w, h, m)
                        return try_connect('localhost')

            # Enter для Join
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                res = try_connect(ip_input.text)
                if res: return res

        clock.tick(30)


# --- ЗАПУСК ---
connection_result = connection_menu()

if not connection_result:
    pygame.quit()
    sys.exit()

client = connection_result
screen = pygame.display.set_mode((WIDTH, HEIGHT))
load_sprites()

thread = threading.Thread(target=receive_data)
thread.start()


def draw_grid():
    if not game_grid or not visible_grid:
        screen.fill((0, 0, 0))
        return

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if y >= len(visible_grid) or x >= len(visible_grid[0]): continue

            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            val = game_grid[y][x]
            vis = visible_grid[y][x]

            if game_state == STATE_MENU:
                screen.blit(sprites['unknown'], rect)
                continue

            if game_state == STATE_GAMEOVER and val == -1:
                screen.blit(sprites['mine'], rect)
            elif vis == 'F':
                screen.blit(sprites['flag'], rect)
            elif vis == False:
                screen.blit(sprites['unknown'], rect)
            elif vis == True:
                if val == -1:
                    screen.blit(sprites['mine_clicked'], rect)
                elif val == 0:
                    screen.blit(sprites['empty'], rect)
                elif val in sprites:
                    screen.blit(sprites[val], rect)


def draw_ui():
    if game_state == STATE_MENU:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        title = font_large.render("MINESWEEPER", True, (0, 255, 0))
        subtitle = font_ui.render("Press SPACE to Start", True, (255, 255, 255))

        screen.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

    elif game_state == STATE_GAMEOVER:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(150)
        s.fill((50, 0, 0))
        screen.blit(s, (0, 0))

        text = font_large.render("GAME OVER", True, (255, 0, 0))
        sub = font_ui.render("Press 'R' to Restart", True, (255, 255, 255))

        screen.blit(text, text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30)))
        screen.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30)))

    elif game_state == STATE_VICTORY:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(150)
        s.fill((0, 50, 0))  # Зелений фон
        screen.blit(s, (0, 0))

        text = font_large.render("VICTORY!", True, (0, 255, 0))
        sub = font_ui.render("Press 'R' to Play Again", True, (255, 255, 255))

        screen.blit(text, text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30)))
        screen.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30)))


clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            client.close()

        if event.type == pygame.KEYDOWN:
            if game_state == STATE_MENU and event.key == pygame.K_SPACE:
                try:
                    client.send(pickle.dumps((0, 0, 99)))
                except:
                    pass

            if (game_state == STATE_GAMEOVER or game_state == STATE_VICTORY) and event.key == pygame.K_r:
                try:
                    client.send(pickle.dumps((0, 0, 88)))
                except:
                    pass

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == STATE_PLAYING:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE

            if gx < GRID_WIDTH and gy < GRID_HEIGHT:
                action = -1
                if event.button == 1:
                    action = 0
                elif event.button == 3:
                    action = 1

                if action != -1:
                    try:
                        client.send(pickle.dumps((gx, gy, action)))
                    except:
                        pass

    draw_grid()
    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
