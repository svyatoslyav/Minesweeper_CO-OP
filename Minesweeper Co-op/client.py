import socket

HEADER = 64
SERVER = "26.8.108.156"
PORT = 5055
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

MSG_DISCONNECT = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(message):
    msg = message.encode(FORMAT)
    msg_len = str(len(msg)).encode()
    msg_len += b' ' * (HEADER - len(msg_len))
    client.send(msg_len)
    client.send(msg)


Connected = True
while Connected:
    msg = input()
    if msg == MSG_DISCONNECT:
        Connected = False
    send(msg)