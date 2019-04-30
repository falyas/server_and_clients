"""Author: Farah Alyasari, 2019 All Rights Reserved.

A player program for the puzzle word game """

import socket
import random
from itertools import zip_longest

#this is a socket object for IPV4 and UDP communication
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 5558
SERVER = (SERVER_ADDR, SERVER_PORT)
MY_ADDR = '127.0.0.1'
MY_PORT = 5587          #can be changed per user
RECV_BUFF_SIZE = 512
SEND_BUFF = ''
MY_ID = 'player'
RESEARCHER_ID = 'researcher'
UBUNTU_ID = 'ubuntu'
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 5
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


def match_letters(PUZZLE_WORD, GUESS):
    """Match LETTERS of two strings, if LETTERS do not match put "_"."""

    correct_and_guess = [(PUZZLE_WORD, GUESS), (PUZZLE_WORD, GUESS)]
    for correct, GUESS in correct_and_guess:
        # If characters in same positions match, then show character, otherwise show `_`
        new_word = ''.join(c if c == g else '_' for c,
                           g in zip_longest(correct, GUESS, fillvalue='_'))
    return new_word

while True:
    USER_INPUT = input(" ")

    #case 1: client demands to exit the program gracefully
    if 'stop' in USER_INPUT.lower():
        #expected SEND_BUFF: client_id->SERVER#<ip>{port}(offline)
        SEND_BUFF = MY_ID+'->'+SERVER_ADDR + '{' + str(MY_PORT) + '}' + '(offline)'
        SOCK.sendto(SEND_BUFF.encode(), SERVER)
        break

    #case 2: player is doing the puzzle word game
    #expected user input: start
    elif 'start' in USER_INPUT.lower():
        #expected SEND_BUFF: client_id->SERVER#<ip>{port}
        SEND_BUFF = MY_ID+'->'+SERVER_ADDR + '{' + str(MY_PORT) + '}'
        SOCK.sendto(SEND_BUFF.encode(), SERVER)
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("Welcome to the UR5 puzzle game challenge, this is the player view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("The game rules are simple:\n")
        print("1 . The puzzle word is 3 to 5 LETTERS long\n")
        print("2 . The puzzle word has no numbers or special characters\n")
        print("3 . Please GUESS according to the puzzle word format\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print(". . . waiting for the researcher to choose a word . . . \n")

        #game in process
        PUZZLE_WORD = ''
        GOT_PUZZLE_WORD = False
        while GOT_PUZZLE_WORD is False:
            #expected: from researcher: {[PUZZLE_WORD]:some message}
            DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
            DATA = DATA.decode()
            if '[PUZZLE_WORD]' in DATA:
                PUZZLE_WORD = find_substring(DATA, ']:', '}')
                GOT_PUZZLE_WORD = True

        print('researcher successfully sent a puzzle word\n')

        GUESS = ' ' #initial value
        SHOW_ONCE = False

        while GUESS.lower() != PUZZLE_WORD.lower():
            GUESS = input("Please enter a GUESS: ")
            DATA_CHECK = (only_letters(GUESS) and
                          length_check(GUESS, MIN_WORD_LENGTH, MAX_WORD_LENGTH))
            print("\n")
            while DATA_CHECK is False:
                GUESS = input("Follow the game rules, enter another GUESS: ")
                DATA_CHECK = (only_letters(GUESS) and
                              length_check(GUESS, MIN_WORD_LENGTH, MAX_WORD_LENGTH))
                print("\n")

            #let users know about the help option
            if (SHOW_ONCE is False) and (GUESS != PUZZLE_WORD):
                print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
                print("By the way, you can request help from the researcher now or later!\n")
                print("You just have to type 'help'\n")
                print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
                SHOW_ONCE = True

            MESSAGE_ID = random_int(MSG_ID_LENGTH, MSG_ID_LOWEST, MSG_ID_HIGHEST)
            MESSAGE_ID = str(MESSAGE_ID)

            if GUESS != 'help':

                #get the correct LETTERS only
                if GUESS != 'help':
                    CORRECT_LETTERS = match_letters(PUZZLE_WORD, GUESS)

                #send the correct LETTERS to Ubuntu
                MESSAGE_ID = random_int(MSG_ID_LENGTH, MSG_ID_LOWEST, MSG_ID_HIGHEST)
                MESSAGE_ID = str(MESSAGE_ID)
                SEND_BUFF = (MY_ID+'->'+ UBUNTU_ID + "#<msg_id:" + MESSAGE_ID +
                             ">{[LETTERS]:" + str(CORRECT_LETTERS) + "}")
                SOCK.sendto(SEND_BUFF.encode(), SERVER)

                #wait to recieve confirmation from SERVER
                DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
                DATA = DATA.decode()
                if 'success' not in DATA:
                    print('LETTERS not successfully forwarded to ubuntu\n')

                #print the correct LETTERS to the player
                print("The shown LETTERS are correct: " + CORRECT_LETTERS)

                #expected format: client_id_1->client_id_2#<msg_id:######>{[GUESS]:some_message}
                SEND_BUFF = (MY_ID+'->'+RESEARCHER_ID+"#<msg_id:"+MESSAGE_ID+
                             ">{[GUESS]:"+str(GUESS)+"}")
                SOCK.sendto(SEND_BUFF.encode(), SERVER)

                #wait to recieve a confirmation from SERVER
                DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
                DATA = DATA.decode()
                if 'success' in DATA:
                    print('GUESS successfully forwarded to the researcher\n')

            elif GUESS == 'help':
                #send HINT request to reseacher

                #expected format: client_id_1->client_id_2#<msg_id:######>{[GUESS]:some_message}
                SEND_BUFF = (MY_ID+'->'+RESEARCHER_ID+"#<msg_id:"+MESSAGE_ID+
                             ">{[HINT]:"+str(GUESS)+"}")
                SOCK.sendto(SEND_BUFF.encode(), SERVER)

                #wait to recieve a confirmation from SERVER
                DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
                DATA = DATA.decode()
                if 'success' in DATA:
                    print('hint request successfully forwarded to the researcher\n')

                #the max HINT lenght is 250 characters = 512 - 262
                #expected: from researcher: {[HINT]:some message}
                DATA, SERVER = SOCK.recvfrom(RECV_BUFF_SIZE)
                DATA = DATA.decode()
                HINT = find_substring(DATA, ']:', '}')
                #an empty sequency evaluates to false
                if not HINT:
                    print("\nthe researcher did not give you a hint")
                else:
                    print("hint: " + HINT + "\n")
            else:
                print("default")

        print("Congratulation, you guessed the word correctly!")

    #case 3: user gives inputs other than stop and start
    else:
        print("\nEnter 'stop' to close the game and 'start' to begin the game")
