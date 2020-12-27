from socket import *
from time import sleep

server_ip = gethostbyname(gethostname())

UDP_DEST_PORT = 13117
BROADCAST = '255.255.255.255'

# 0xfeedbeef - magic cookie, 0x2 - type, port - 1300 -> 0x0514
msg_bytes = [0xfe, 0xed, 0xbe, 0xef, 0x02, 0x05, 0x14]
# convert to byte array
msg = bytes(msg_bytes)
print(msg)
sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP
sock_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

print('Server started, listening on IP address', server_ip)

# send broadcast through udp every one sec
for x in range(10):
    sleep(1)
    sock_udp.sendto(msg, (BROADCAST, UDP_DEST_PORT))
