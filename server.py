from socket import *
from time import sleep

server_ip = gethostbyname(gethostname())

# send broadcast through udp every one sec
UDP_DEST_PORT = 13117
BROADCAST = '255.255.255.255'
msg_bytes = [0xfe, 0xed, 0xbe, 0xef, 0x2, 50]
msg = bytes(msg_bytes)
print(msg)
sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP
sock_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

print('Server started, listening on IP address', server_ip)

for x in range(10):
    sleep(1)
    sock_udp.sendto(msg, (BROADCAST, UDP_DEST_PORT))

"""
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

while 1:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024)
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence)
    connectionSocket.close()
"""
