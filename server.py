from socket import *
from time import sleep
import threading
import random
import sys
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


def clear_data(procs, sockets, c_map, group1, group2):
    c_map.clear()
    for sock in sockets:
        sock.close()
    procs.clear()
    group1.clear()
    group2.clear()
    sockets.clear()


def get_mvp(c_map, winning_group):
    sys.stdout.write(BOLD + BLUE)
    best = 0
    mvp = ""
    for hostName in winning_group:
        currVal = c_map[hostName]
        if currVal > best:
            mvp = winning_group[hostName]
            best = currVal
    return "Best Team Played: " + mvp + "\n" + \
        "Smashing " + str(best) + " times!\n"


def declare_winner(c_map, group1, group2):
    g1 = 0
    g2 = 0
    for hostName in group1:
        g1 += c_map[hostName]
    for hostName in group2:
        g2 += c_map[hostName]
    sys.stdout.write(GREEN)
    msg = "Game over!\nGroup 1 typed in" + \
        str(g1) + "characters.\nGroup 2 typed in" + str(g2) + "characters.\n"
    if g1 > g2:
        msg += "Group 1 wins!\nCongratulations to the winners:\n==\n"
        for n in group1.values():
            msg += (n + "\n")
        msg += get_mvp(c_map, group1)
    elif g2 > g1:
        msg += "Group 2 wins!\nCongratulations to the winners:\n==\n"
        for n in group2.values():
            msg += (n + "\n")
        msg += get_mvp(c_map, group2)
    else:
        msg += "Its a draw! Thanks for participating!"
    return msg


def listen(sock_tcp, procs, sockets, c_map, kill_acc, kill_all):
    while 1:
        if not kill_acc:
            try:
                sock, addr = sock_tcp.accept()
                sock.settimeout(1)
                clientId = addr[0] + str(addr[1])
                x = threading.Thread(
                    target=thread_job, args=(clientId, sock, c_map, kill_all))
                procs[clientId] = x
                sockets.append(sock)
                c_map[clientId] = 0
            except:
                continue


def thread_job(clientId, socket, c_map, kill_all):
    while not kill_all:
        try:
            msg = socket.recv(1024)
            length = len(msg)
            if length == 0:
                break
            c_map[clientId] = c_map[clientId] + len(msg)
        except:
            continue


def start_game(sockets, procs):
    msg = 'Welcome to Keyboard Spamming Battle Royale.\n'
    msg += "Group 1:\n==\n"
    for n in group1.values():
        msg += n
    msg += "Group 2:\n==\n"
    for n in group2.values():
        msg += n
    msg += 'Start pressing keys on your keyboard as fast as you can!!'
    encoded = msg.encode()
    for sock in sockets:
        sock.send(encoded)
    for proc in procs.values():
        proc.start()
    sleep(10)


if __name__ == "__main__":
    procs = {}
    sockets = []
    c_map = {}  # {addr:numberOfHits}
    group1 = {}  # {addr:name}
    group2 = {}  # {addr:name}
    server_ip = get_if_addr(NETWORK)  # gethostbyname(gethostname())
    SERVER_PORT = 2012
    UDP_DEST_PORT = 13117
    BROADCAST = '255.255.255.255'

    # 0xfeedbeef - magic cookie, 0x2 - type, port - 1300 -> 0x0514
    msg_bytes = [0xfe, 0xed, 0xbe, 0xef, 0x02, 0x05, 0x14]
    # convert to byte array
    msg = struct.pack('Ibh', 0xfeedbeef, 2, SERVER_PORT)
    sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP
    sock_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock_tcp = socket(AF_INET, SOCK_STREAM)
    sock_tcp.settimeout(1)
    sock_tcp.bind((server_ip, SERVER_PORT))
    sock_tcp.listen(5)
    sys.stdout.write(CYAN)
    print('Server started, listening on IP address', server_ip)
    while 1:
        # accept connections for 10 secs in t_acc thread
        kill_acc = False
        kill_all = False
        t_acc = threading.Thread(
            target=listen, args=(sock_tcp, procs, sockets, c_map, kill_acc, kill_all))
        t_acc.start()
        # send broadcast through udp every one sec
        for x in range(10):
            sleep(1)
            sock_udp.sendto(msg, (BROADCAST, UDP_DEST_PORT))
        kill_acc = True
        # add all names to list
        for s in sockets:
            peer = s.getpeername()
            clientId = peer[0]+str(peer[1])
            try:
                # if fails, skip client and remove his socket
                msg = s.recv(1024)
            except:
                sockets.remove(s)  # clear user socket
                del procs[clientId]  # clear user process
                continue            # go read from next user
            if random.randint(1, 2) == 1:
                group1[clientId] = msg.decode()
            else:
                group2[clientId] = msg.decode()
        # start game for 10 seconds
        start_game(sockets, procs)
        kill_all = True
        # declare winner
        end_msg = declare_winner(c_map, group1, group2)
        # send end of game msg
        for s in sockets:
            try:
                s.send(end_msg.encode())
            except:
                continue
        # clear all previous game data
        clear_data(procs, sockets, c_map, group1, group2)
        sys.stdout.write(CYAN)
        print("Game over, sending out offer requests...")
