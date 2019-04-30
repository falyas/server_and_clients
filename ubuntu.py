"""Author: Farah Alyasari, 2019 All Rights Reserved.

A client program to store puzzle words in a local desk file

such that the ROS Python node is able to open the local desk file

and retrieve the correct LETTERS to write on the whiteboard """

import socket
import random

#this is a socket object for IPV4 and UDP communication
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MY_ADDR = '127.0.0.1'
MY_PORT = 5578
SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 5558
SERVER = (SERVER_ADDR, SERVER_PORT)
SOCK.connect(SERVER)
RECV_BUFF_SIZE = 512
SEND_BUFF = ''
MY_ID = 'ubuntu'


def find_substring(astring, first, last):
    """use to extract information from the DATA recieved it will always extract

    the first and the last which show up earlier in the string."""

    try:
        start = astring.index(first) + len(first)
        if last == 'end_of_string':
            end = len(astring)
        else:
            end = astring.index(last, start)
            return astring[start:end]
    except ValueError:
        return 'error_s'

def random_int(length, lowest, highest):
    """Generates a random number to send in the header of the datagram."""

    string_of_ints = ''
    for _ in range(length):
        string_of_ints += str(random.randint(lowest, highest))
    val = int(string_of_ints)
    return val

while True:
    USER_INPUT = input(" ")

    #case 1: client demands to exit the program gracefully
    if USER_INPUT.lower() == 'stop':
        break

    #case 2: researcher is hosting the puzzle word game
    #expected user input: start
    elif USER_INPUT.lower() == 'start':

        #expected SEND_BUFF: client_id->SERVER#<ip>{port}
        SEND_BUFF = MY_ID+'->'+SERVER_ADDR + '{' + str(MY_PORT) + '}'
        SOCK.sendto(SEND_BUFF.encode(), SERVER)

        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")
        print("Welcome to the UR5 puzzle game challenge,\n")
        print("this is the ubuntu view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")
        print("This client has two jobs:\n")
        print("1 . Recieve correct LETTERS from the SERVER\n")
        print("2 . Store the correct LETTERS inside a file\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")

        while True:
            DATA, SERVER_ADDR = SOCK.recvfrom(RECV_BUFF_SIZE)
            DATA = DATA.decode()
            LETTERS = ''
            if 'LETTERS' in DATA:
                #expected format: from player: {[LETTERS]:some message}
                LETTERS = find_substring(DATA, ']:', '}')
                print("letters recieved: " + LETTERS)
                LETTERS_FILE = open("letters.txt", "w+")
                LETTERS_FILE.write(LETTERS)
                LETTERS_FILE.close()
                print("letters saved")
            else:
                print("no letters recieved")
