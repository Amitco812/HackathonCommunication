from socket import *

print('Client started, listening for offer requests...')
server_port = 13117
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', server_port))
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

message, server_address = clientSocket.recvfrom(2048)
print('Received offer from ,', server_address, 'attempting to connect...')
length = len(message)
if length != 7:
    print('deprecated message!')
if message[0] != 0xfe or message[1] != 0xed or message[2] != 0xbe or message[3] != 0xef:
    print('error in message cookie, reject message!')
if message[4] != 0x2:
    print('error in message type!')
suggestedPort = int.from_bytes(message[5:], "big")
print(suggestedPort)
