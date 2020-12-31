from socket import *
import time
import signal
import sys
import tty
import termios
import struct
from scapy.arch import get_if_addr

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"
NETWORK = 'eth2'
GAME_TIME = 10
BUFFER_SIZE = 1024
MESSAGE_TYPE = 0x2
MAGIC_COOKIE = 0xfeedbeef


def interrupted(signum, frame):
    raise Exception("timeout")

# retrieves one character from user, regardless of user input (doesn't require '\n')
def getch():
    fd = sys.stdin.fileno()                 # file descriptor of STDIN
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print(ch)  # just for ui needs...
    return ch


if __name__ == "__main__":
    sys.stdout.write(CYAN)
    print('Client started, listening for offer requests...')
    serverPort = 13117
    # open udp socket to listen to broadcasts
    clientUdpSocket = socket(AF_INET, SOCK_DGRAM)
    clientUdpSocket.bind(('', serverPort))
    # initiate client UDP socket
    clientUdpSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientUdpSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    signal.signal(signal.SIGALRM, interrupted)
    while True:
        try:
            # receive offer, blocking method
            offer, serverName = clientUdpSocket.recvfrom(BUFFER_SIZE)
            cookie, mtype, pnum = struct.unpack('Ibh', offer)
            # message received, open tcp connection
            hostName = serverName[0]
            print('Received offer from,', hostName,
                  'attempting to connect...')
            # corrupted cookie
            if cookie != MAGIC_COOKIE:
                sys.stdout.write(RED)
                print('error in message cookie, reject message!')
                continue
            # corrupted type
            if mtype != MESSAGE_TYPE:
                sys.stdout.write(RED)
                print('error in message type!')
                continue
            # decode suggested port
            sys.stdout.write(CYAN)
            # open tcp connection
            clientTcpSocket = socket(AF_INET, SOCK_STREAM)  # tcp socket
            clientTcpSocket.connect((hostName, pnum))  # handShake
            groupName = 'Hadorbanim\n'
            clientTcpSocket.send(groupName.encode())  # send group name
            clientTcpSocket.settimeout(GAME_TIME)  # set time out for bad servers
            msgOfNames = clientTcpSocket.recv(1024)  # get names of all groups
            print(msgOfNames.decode())  # print the message
            t_end = time.time() + GAME_TIME
            sys.stdout.write(GREEN)
            # while code block - reads characters from
            # user and sends each one to the server over TCP
            while time.time() < t_end:
                try:
                    signal.alarm(1)
                    ch = getch()
                    signal.alarm(0)
                    clientTcpSocket.send(ch.encode())
                except:
                    continue
            try:
                sys.stdout.write(BLUE) # ANSI color
                end_msg = clientTcpSocket.recv(2*BUFFER_SIZE)
                print(end_msg.decode())
            except:
                sys.stdout.write(CYAN)
            finally:
                clientTcpSocket.close() # ALWAYS close TCP socket when done
            sys.stdout.write(CYAN)
            print("Server disconnected, listening for offer requests...")
        except:
            continue
