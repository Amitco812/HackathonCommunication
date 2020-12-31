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
NETWORK = 'eth1'
GAME_TIME = 10
PRE_GAME_WAIT_TIME = 10
MESSAGE_TYPE = 0x2
MAGIC_COOKIE = 0xfeedbeef
BUFFER_SIZE = 1024
SERVER_PORT = 2012
UDP_DEST_PORT = 13117

# clears all data structures 
def clear_data(procs, sockets, c_map, group1, group2):
    c_map.clear()
    for sock in sockets:
        sock.close()
    procs.clear()
    group1.clear()
    group2.clear()
    sockets.clear()

# a game statistic- computes most typing client
def get_mvp(c_map, winning_group):
    sys.stdout.write(BOLD + BLUE)
    best = 0
    mvp = ""
    # finds best clicking client
    for hostName in winning_group:
        currVal = c_map[hostName]  # current client's score  
        if currVal > best:
            mvp = winning_group[hostName]
            best = currVal         # saves best values of all iterations 
    return "Best Team Played: " + mvp + "\n" + \
        "Smashing " + str(best) + " times!\n"

# creates last game's relevant "game over" message 
def generate_winner_message(c_map, group1, group2):
    g1 = 0
    g2 = 0
    # loops agreggate group 1 and group 2's scores.
    for hostName in group1:
        g1 += c_map[hostName]
    for hostName in group2:
        g2 += c_map[hostName]
    sys.stdout.write(GREEN)
    msg = "Game over!\nGroup 1 typed in " + \
        str(g1) + " characters.\nGroup 2 typed in " + \
        str(g2) + " characters.\n"
        # all last announcment scenarious (win\lose\draw)
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

# function of thread that accepts client connections over tcp
def listen(sock_tcp, procs, sockets, c_map, kill_acc, kill_all):
    while True:
        # continue to run if thread is annonated alive
        if not kill_acc:
            try:
                sock, addr = sock_tcp.accept() # recieve connection
                sock.settimeout(1) # so thread can check if it needs to finish
                clientId = addr[0] + str(addr[1])
                print("client connected with id: ", clientId)
                x = threading.Thread(
                    target=thread_job, args=(clientId, sock, c_map, kill_all))
                procs[clientId] = x
                sockets.append(sock) # thread build
                c_map[clientId] = 0
            except:
                continue

# function of all threads that recieve own's client typing while game
#  (every thread has one client connection)
def thread_job(clientId, socket, c_map, kill_all):
    # continue to run if thread is annonated alive
    while not kill_all:
        try:
            msg = socket.recv(BUFFER_SIZE)
            length = len(msg)
            if length == 0: # error- ignore message
                break
            c_map[clientId] = c_map[clientId] + len(msg)
        except:
            continue

# starts the game.
# provokes all connections to be run by their threads. 
def start_game(sockets, procs):
    # generates starting message with all participents names
    msg = 'Welcome to Keyboard Spamming Battle Royale.\n'
    msg += "Group 1:\n==\n"
    for n in group1.values():
        msg += n
    msg += "Group 2:\n==\n"
    for n in group2.values():
        msg += n
    msg += 'Start pressing keys on your keyboard as fast as you can!!'
    encoded = msg.encode()
    # send starting message to every client
    for sock in sockets:
        sock.send(encoded)
    # run all threads to recieve messages from clients
    for proc in procs.values():
        proc.start()
    print("Game on! 10 secs..")
    # main thread waits for the game to finish GAME_TIME seconds
    sleep(GAME_TIME) 


if __name__ == "__main__":
    procs = {}
    sockets = []
    c_map = {}  # {addr:numberOfHits}
    group1 = {}  # {addr:name}
    group2 = {}  # {addr:name}
    server_ip = get_if_addr(NETWORK)  # gethostbyname(gethostname())
    

    # convert to byte array
    msg = struct.pack('Ibh', MAGIC_COOKIE, MESSAGE_TYPE, SERVER_PORT)
    # open UDP socket in order to send broadcasts
    sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP
    sock_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    # open TCP socket in order to accept new client connections
    sock_tcp = socket(AF_INET, SOCK_STREAM)
    sock_tcp.settimeout(1)
    sock_tcp.bind(('', SERVER_PORT))
    sock_tcp.listen()
    sys.stdout.write(CYAN) # ANSI color change
    print('Server started, listening on IP address', server_ip)
    while True:
        # accept connections for GAME_TIME secs in t_acc thread
        kill_acc = False
        kill_all = False
        t_acc = threading.Thread(
            target=listen, args=(sock_tcp, procs, sockets, c_map, kill_acc, kill_all))
        t_acc.start()
        # send broadcast through udp every one sec for PRE_GAME_WAIT_TIME secs 
        for x in range(PRE_GAME_WAIT_TIME):
            sleep(1)
            sock_udp.sendto(msg, ('<broadcast>', UDP_DEST_PORT))
        kill_acc = True
        # add all names to list
        for s in sockets:
            peer = s.getpeername()
            clientId = peer[0]+str(peer[1])
            try:
                # if fails, skip client and remove his socket
                msg = s.recv(BUFFER_SIZE)
            except:
                print("Misbehaving user, no name sent")
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
        end_msg = generate_winner_message(c_map, group1, group2)
        # send end of game msg
        for s in sockets:
            try:
                s.send(end_msg.encode())
            except:
                print("Client closed socket too eraly")
                continue
        # clear all previous game data
        clear_data(procs, sockets, c_map, group1, group2)
        sys.stdout.write(CYAN)
        print("Game over, sending out offer requests...")
