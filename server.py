"""Author: Farah Alyasari, 2019 All Rights Reserved.

This server forwards UDP packets """

import socket
import string
import random
from dataclasses import dataclass

#this is a SOCKET object for IPV4 and UDP communication
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_ADDR = '127.0.0.1'
CLIENT_ADDR = '127.0.0.1'
SERVER_PORT = 5558
RECV_BUFF_SIZE = 1024
SEND_BUFF = ''

#using loop back ADDRESS on the local machine with an unreserved port number
#Running two processes using TCP/IP SOCKET for communication on one computer
#is basically equivalent to running two processes on two computers individually.
#So it does not matter and the program should work either way.
ADDRESS = (SERVER_ADDR, SERVER_PORT)
print('starting up on {} port {}'.format(*ADDRESS))
SOCK.bind(ADDRESS)


@dataclass
class Session:
    """This is a class tracks the login and logoff activity of clients."""
    state: str
    client_id: str
    CLIENT_ADDR: str
    CLIENT_PORT: int
    def switch_to_online(self):
        """Switch user to online when they connect to the server"""
        self.state = 'online'
    def switch_to_offline(self):
        """Switch user to offline when they send a signal in the UDP header"""
        self.state = 'offline'

#an array of Session objects
SESSION_LIST = []

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

def get_unique_connection_key(size=6, chars=string.ascii_uppercase + string.digits):
    """Used to send back a unique connection key each time a user logs in."""
    return ''.join(random.choice(chars) for _ in range(size))

while True:

    DATA, FROM_ADDR = SOCK.recvfrom(RECV_BUFF_SIZE)
    DATA = DATA.decode()
    FROM_ID = find_substring(DATA, '', '->')
    FROM_PORT = find_substring(DATA, '{', '}')
    NEW_SESSION = Session('online', FROM_ID, FROM_ADDR, FROM_PORT)
    SESSION_LIST.append(NEW_SESSION)
    print('the ' + FROM_ID + ' is online')

    #case 1: a client wants to forward a message to another client
    #expected DATA: client_id_1->client_id_2#<msg_id:######>{some_message}
    if 'msg_id' in DATA:
        #extract the TO_ID and TO_PORT to forward the message to the desired client
        TO_ID = find_substring(DATA, '->', '#')
        FROM_MSG_ID = find_substring(DATA, ':', '>')
        TO_PORT = 0         #initial value
        TO_STATE = ''       #initial value
        TO_ADDR = ''
        for x in SESSION_LIST:
            if x.client_id == TO_ID:
                TO_PORT = x.CLIENT_PORT
                TO_STATE = x.state
                TO_ADDR = x.CLIENT_ADDR
                print('the ' + TO_ID + ' is ' + TO_STATE)
                break
        if TO_STATE != 'online':
            #tell the from client that the to client is offline
            #expected SEND_BUFF: server->client_id<msg_id>Error: destination offline!
            SEND_BUFF = ('server->' + FROM_ID + '#<' +
                         FROM_MSG_ID + '>destination is offline!')
            SOCK.sendto(SEND_BUFF.encode(), FROM_ADDR)
            print('the to client ' + TO_ID + ' is offline')
        else:
            #extract the message to be forwarded and send it to the to client
            #expected format: client_id_1->client_id_2#<msg_id:######>{some_message}
            print(DATA)
            FORWARD_MESSAGE = find_substring(DATA, '{', '}')
            SEND_BUFF = 'from ' + FROM_ID + ':{'+ str(FORWARD_MESSAGE)+'}'
            SOCK.sendto(SEND_BUFF.encode(), TO_ADDR)
            #echo the message to the sending client. Note this does not necessarly mean the
            #message was successfully delivered to the client, it just means that it was
            #successfully delivered to the server and that the server forwarded it
            FROM_MSG_ID = find_substring(DATA, '<', '>')
            SEND_BUFF = ('server->'+ TO_ID + '#<'+ FROM_MSG_ID+'>success')
            print(SEND_BUFF)
            SOCK.sendto(SEND_BUFF.encode(), FROM_ADDR)

    elif 'offline' in DATA:
        #turn this client to offline
        for x in SESSION_LIST:
            if (x.client_id == FROM_ID) and (x.CLIENT_PORT == FROM_PORT):
                x.switch_to_offline()
                print('the ' + FROM_ID + ' is ' + x.state)
                break
