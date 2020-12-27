from socket import *
# serverName = ‘hostname’
server_port = 13117
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', server_port))
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

message, server_address = clientSocket.recvfrom(2048)
print(message, server_address)

"""
serverName = 'amitAmir'
serverPort = 13117
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))
sentence = raw_input('Input lowercase sentence: ')
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
print('From Server: ', modifiedSentence)
clientSocket.close()
"""
