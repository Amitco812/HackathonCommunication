from socket import *
import time
import signal
import sys, tty, termios


def interrupted(signum, frame):
    raise Exception("timeout")


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print(ch) #just for ui needs...
    return ch

if __name__ == "__main__":
    print('Client started, listening for offer requests...')
    serverPort = 13117
    # open udp socket to listen to broadcasts
    clientUdpSocket = socket(AF_INET, SOCK_DGRAM)
    clientUdpSocket.bind(('', serverPort))
    # initiate client socket
    clientUdpSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientUdpSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    signal.signal(signal.SIGALRM, interrupted)
    while 1:
        try:
            # receive offer, blocking method
            offer, serverName = clientUdpSocket.recvfrom(1024)
            # message received, open tcp connection
            hostName = serverName[0]
            print('Received offer from,', hostName,
                  'attempting to connect...')
            length = len(offer)
            # message length expected - 4 bytes cookie, 1 byte type, 2 byte port
            if length != 7:
                print('deprecated message!')
                continue
            # corrupted cookie
            if offer[0] != 0xfe or offer[1] != 0xed or offer[2] != 0xbe or offer[3] != 0xef:
                print('error in message cookie, reject message!')
                continue
            # corrupted type
            if offer[4] != 0x2:
                print('error in message type!')
                continue
            # decode suggested port
            suggestedPort = int.from_bytes(offer[5:], "big")
            # open tcp connection
            clientTcpSocket = socket(AF_INET, SOCK_STREAM)  # tcp socket
            clientTcpSocket.connect((hostName, suggestedPort))  # handShake
            groupName = 'Hadorbanim\n'
            clientTcpSocket.send(groupName.encode())  # send group name
            msgOfNames = clientTcpSocket.recv(1024)  # get names of all groups
            print(msgOfNames.decode())  # print the message
            t_end = time.time() + 10
            try:
                while time.time() < t_end:
                    try:
                        signal.alarm(1)
                        ch = getch()
                        signal.alarm(0)
                        clientTcpSocket.send(ch.encode())
                    except:
                        continue
            finally:
                clientTcpSocket.close()
            print("Server disconnected, listening for offer requests...")
        except:
            continue

