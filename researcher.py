"""Author: Farah Alyasari, 2019 All Rights Reserved.

This researcher is used for the puzzle word game """

import socket
import random

#this is a socket object for IPV4 and UDP communication
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 5558
SERVER = (SERVER_ADDR, SERVER_PORT)
MY_ADDR = '127.0.0.1'
MY_PORT = 5592
RECV_BUFF_SIZE = 512
SEND_BUFF = ''
MY_ID = 'researcher'
TO_ID = 'player'
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 5
MIN_HINT_LENGTH = 0
MAX_HINT_LENGTH = 250
MSG_ID_LENGTH = 10
MSG_ID_LOWEST = 1
MSG_ID_HIGHEST = 9

#connect the socket to the SERVER to be able to send to the SERVER
SOCK.connect(SERVER)

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

def only_letters(word):
    """Used to check the puzzle word and hint format."""
    word = str(word)
    return word.isalpha()

def length_check(word, min_length, max_length):
    """Used to check the puzzle word length format."""
    word = str(word)
    if min_length <= len(word) <= max_length:
        return True
    return False

while True:
    USER_INPUT = input(" ")

    #case 1: client demands to exit the program gracefully
    if 'stop' in USER_INPUT.lower():
        #expected SEND_BUFF: client_id->SERVER#<ip>{port}(offline)
        SEND_BUFF = MY_ID+'->'+SERVER_ADDR + '{' + str(MY_PORT) + '}' + '(offline)'
        SOCK.sendto(SEND_BUFF.encode(), SERVER)
        break

    #case 2: researcher is hosting the puzzle word game
    #expected user input: start
    elif 'start' in USER_INPUT.lower():
        #expected SEND_BUFF: client_id->SERVER#<ip>{port}
        SEND_BUFF = MY_ID+'->'+SERVER_ADDR + '{' + str(MY_PORT) + '}' + ''
        SOCK.sendto(SEND_BUFF.encode(), SERVER)

        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("Welcome to the UR5 puzzle game challenge, this is the researcher view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("The game rules are simple:\n")
        print("1 . Choose a puzzle word between "
              + str(MIN_WORD_LENGTH) +" to " + str(MAX_WORD_LENGTH) + " letters long\n")
        print("2 . Don't use numbers or special characters\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        PUZZLE_WORD = input("Please enter a puzzle word: ")
        DATA_CHECK = (only_letters(PUZZLE_WORD) and
                      length_check(PUZZLE_WORD, MIN_WORD_LENGTH, MAX_WORD_LENGTH))
        print("\n")
        while DATA_CHECK is False:
            PUZZLE_WORD = input("\nPlease follow the game rules! Try another puzzle word: ")
            DATA_CHECK = (only_letters(PUZZLE_WORD) and
                          length_check(PUZZLE_WORD, MIN_WORD_LENGTH, MAX_WORD_LENGTH))
            print("\n")
        MESSAGE_ID = random_int(MSG_ID_LENGTH, MSG_ID_LOWEST, MSG_ID_HIGHEST)
        MESSAGE_ID = str(MESSAGE_ID)
        #expected format: client_id_1->client_id_2#<msg_id:######>{[PUZZLE_WORD]:some_message}
        SEND_BUFF = (MY_ID+'->'+TO_ID+"#<msg_id:"+MESSAGE_ID+
                     ">{[PUZZLE_WORD]:"+str(PUZZLE_WORD)+"}")
        SOCK.sendto(SEND_BUFF.encode(), SERVER)

        #wait to recieve a confirmation from SERVER that the message was forwarded successfully
        DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
        DATA = DATA.decode()
        if 'success' in DATA:
            print('puzzle word successfully forwarded to the player\n')
        #else: the to client is offline
        else:
            break

        print('... waiting for the player to guess the word ... \n')

        #game in process, some initial values
        GUESS_COUNT = 1
        HINT_COUNT = 1
        GUESS = ''
        while PUZZLE_WORD.lower() != GUESS.lower():
            DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
            DATA = DATA.decode()

            #expected format: from player:{[GUESS]:some message} or from player:{[HINT]:help}
            if '[GUESS]' in DATA:
                GUESS = find_substring(DATA, ']:', '}')
                GUESS_COUNT = GUESS_COUNT + 1
                print('('+ str(GUESS_COUNT)+') The player guessed: ' + GUESS)

            elif '[HINT]' in DATA:
                HINT_COUNT = HINT_COUNT + 1
                print("\n["+str(HINT_COUNT)+"] Player is requesting a hint!")
                HINT = input("\nPlease keep your hint under "+
                             str(MAX_HINT_LENGTH) + " letters: ")
                HINT_CHECK = length_check(HINT, MIN_HINT_LENGTH, MAX_HINT_LENGTH)
                while HINT_CHECK is False:
                    HINT_CHECK = input("\nSorry, hint must be under " + str(MAX_HINT_LENGTH) + " letters: ")
                    HINT_CHECK = (only_letters(PUZZLE_WORD) and
                                  length_check(HINT_CHECK, MIN_HINT_LENGTH, MAX_HINT_LENGTH))
                    print("\n")
                MESSAGE_ID = random_int(MSG_ID_LENGTH, MSG_ID_LOWEST, MSG_ID_HIGHEST)
                MESSAGE_ID = str(MESSAGE_ID)
                #expected format: client_id_1->client_id_2#<msg_id:######>{[HINT]:some_message}
                SEND_BUFF = MY_ID+'->'+TO_ID+"#<msg_id:"+MESSAGE_ID+">{[HINT]:"+str(HINT)+"}"
                SOCK.sendto(SEND_BUFF.encode(), SERVER)
            elif 'success' in DATA:
                print("\nhint successfully forwarded to player")
            else:
                print("\nunexpected message from the server")

        print("\nthe player guessed the word correctly")

    #case 3: user gives inputs other than stop and start
    else:
        print("\nEnter 'stop' to close the game and 'start' to begin the game")
