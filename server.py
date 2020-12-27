from socket import *
from time import sleep
import multiprocessing
import random

procs = []
sockets = []
c_map = {}  # {addr:numberOfHits}
group1 = {}  # {addr:name}
group2 = {}  # {addr:name}


def clear_data():
    c_map.clear()
    for sock in sockets:
        sock.close()
    for process in procs:
        process.terminate()
    procs.clear()
    group1.clear()
    group2.clear()


def declare_winner():
    for ent in c_map:
        print(ent)


def listen(sock_tcp):
    while 1:
        sock, addr = sock_tcp.accept()
        x = multiprocessing.Process(target=thread_job, args=(addr, sock))
        procs.append(x)
        sockets.append(sock)
        c_map[addr] = 0


def thread_job(addr, socket):
    while 1:
        msg = socket.recv(1024)
        c_map[addr] = c_map[addr] + len(msg)


def start_game():
    msg = 'Welcome to Keyboard Spamming Battle Royale.\n'
    msg += "Group 1:\n==\n"
    for n in group1.values():
        msg += n
    msg += "Group 2:\n==\n"
    for n in group2.values():
        msg += n
    msg += 'Start pressing keys on your keyboard as fast as you can!!'

    for sock in sockets:
        sock.send(msg.encode())
    for proc in procs:
        proc.start()


if __name__ == "__main__":
    server_ip = gethostbyname(gethostname())
    SERVER_PORT = 1300
    UDP_DEST_PORT = 13117
    BROADCAST = '255.255.255.255'

    # 0xfeedbeef - magic cookie, 0x2 - type, port - 1300 -> 0x0514
    msg_bytes = [0xfe, 0xed, 0xbe, 0xef, 0x02, 0x05, 0x14]
    # convert to byte array
    msg = bytes(msg_bytes)
    sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP
    #sock_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock_tcp = socket(AF_INET, SOCK_STREAM)
    sock_tcp.bind(('', SERVER_PORT))
    sock_tcp.listen(5)

    while 1:
        # accept connections for 10 secs in t_acc thread
        print('Server started, listening on IP address', server_ip)
        t_acc = multiprocessing.Process(target=listen, args=(sock_tcp,))
        t_acc.start()
        # send broadcast through udp every one sec
        for x in range(10):
            sleep(1)
            sock_udp.sendto(msg, (BROADCAST, UDP_DEST_PORT))
        t_acc.terminate()
        # add all names to list
        for s in sockets:
            print(s.getpeername(), s.getsockname())
            msg = s.recv(1024)
            if random.randint(1, 2) == 1:
                group1[s.getpeername()] = msg.decode()
            else:
                group2[s.getpeername()] = msg.decode()
        # start game for 10 seconds
        start_game()
        # declare winner
        declare_winner()
        # clear all previous game data
        clear_data()
