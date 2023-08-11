import socket
from time import sleep
from random import randint
IP = "127.0.0.1"
PORT = 5005

message = ""

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

print(f"IP:{IP}\nPORT:{PORT}")
for i in range(50):
    message = bytes(str(i), 'utf-8')
    sock.sendto(message,(IP,PORT))
    print(f"Sent:{i}")
    sleep(randint(1,3))
