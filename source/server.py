import socket
import threading
import pickle
import random
import sys

sys.setrecursionlimit(10000)  # Збільшуємо ліміт ще більше для великих полів

HOST = ''
PORT = 5555

# --- ТЕПЕР ЦЕ ЗМІННІ ЗА ЗАМОВЧУВАННЯМ ---
GRID_WIDTH = 20
GRID_HEIGHT = 15
MINES_COUNT = 40

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

game_grid = []
visible_grid = []
game_state = STATE_MENU
clients = []
server_socket = None


def generate_grid():
    global game_grid, visible_grid, game_state
    game_state = STATE_MENU
    visible_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    game_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    mines = 0
    # Захист від зависання: не більше мін, ніж клітинок - 1
    safe_mines_count = min(MINES_COUNT, (GRID_WIDTH * GRID_HEIGHT) - 1)

    while mines < safe_mines_count:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if game_grid[y][x] != -1:
            game_grid[y][x] = -1
            mines += 1
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and game_grid[ny][nx] != -1:
                        game_grid[ny][nx] += 1


def reveal_all_mines():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game_grid[y][x] == -1:
                visible_grid[y][x] = True


def reveal_cell(x, y):
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT): return
    if visible_grid[y][x] is True or visible_grid[y][x] == 'F': return

    visible_grid[y][x] = True
    if game_grid[y][x] == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    reveal_cell(x + dx, y + dy)


def broadcast():
    data = pickle.dumps((game_grid, visible_grid, game_state))
    for client in clients:
        try:
            client.send(data)
        except:
            if client in clients: clients.remove(client)


def handle_client(client_socket):
    global game_state
    try:
        client_socket.send(pickle.dumps({'w': GRID_WIDTH, 'h': GRID_HEIGHT}))
        client_socket.send(pickle.dumps((game_grid, visible_grid, game_state)))
    except:
        return

    while True:
        try:
            data = client_socket.recv(1024)
            if not data: break
            x, y, action = pickle.loads(data)

            if action == 99 and game_state == STATE_MENU:
                generate_grid()
                game_state = STATE_PLAYING
                broadcast()
                continue

            if action == 88 and game_state == STATE_GAMEOVER:
                generate_grid()
                game_state = STATE_PLAYING
                broadcast()
                continue

            if game_state == STATE_PLAYING:
                if action == 0:
                    if visible_grid[y][x] == 'F': continue
                    if game_grid[y][x] == -1:
                        game_state = STATE_GAMEOVER
                        reveal_all_mines()
                    else:
                        reveal_cell(x, y)
                elif action == 1:
                    if visible_grid[y][x] == False:
                        visible_grid[y][x] = 'F'
                    elif visible_grid[y][x] == 'F':
                        visible_grid[y][x] = False
                broadcast()
        except:
            break
    if client_socket in clients: clients.remove(client_socket)
    client_socket.close()


# --- ОНОВЛЕНА ФУНКЦІЯ ЗАПУСКУ ---
def start_server(w=20, h=15, m=40):
    """Приймає параметри для створення поля"""
    global server_socket, GRID_WIDTH, GRID_HEIGHT, MINES_COUNT

    # Оновлюємо глобальні налаштування
    GRID_WIDTH = w
    GRID_HEIGHT = h
    MINES_COUNT = m

    generate_grid()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Запущено: {GRID_WIDTH}x{GRID_HEIGHT}, Мін: {MINES_COUNT}")

        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            thread = threading.Thread(target=handle_client, args=(client_socket,))
            thread.daemon = True
            thread.start()
    except OSError as e:
        print(f"[SERVER] Помилка: {e}")


if __name__ == "__main__":
    start_server()