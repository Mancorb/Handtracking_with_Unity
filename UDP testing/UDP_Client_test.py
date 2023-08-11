import socket
from datetime import datetime
import threading

def sendInfo(IP,PORT, ID):
    print(f"IP:{IP}\nPORT:{PORT}")

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    for i in range(10):
        message = bytes(str(i) + " ID:"+str(ID) + " "+str(current_time), 'utf-8')
        sock.sendto(message,(IP,PORT))
    

IP = "127.0.0.1"
PORT = 5005

message = ""

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
threads = []

for i in range(2):
    t=threading.Thread(target=sendInfo,args=(IP,PORT,i))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

