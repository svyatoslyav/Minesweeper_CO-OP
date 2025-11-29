import socket
import threading


HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5055
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

MSG_DISCONNECT = "!DISCONNECT"

print(SERVER)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def HandleClient(conn, addr):
    print(f"new connection at {addr} \n")

    connected = True
    while connected:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)

            msg = conn.recv(msg_len).decode(FORMAT)
            if msg == MSG_DISCONNECT:
                connected = False
                print(f"{addr} disconnected")
                print(f"active connections:{threading.active_count() - 1}\n")
            else:
                print(f"{addr} said:{msg}")

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=HandleClient, args=(conn, addr))
        thread.start()
        print(f"active connections:{threading.active_count() - 1}\n")

start()