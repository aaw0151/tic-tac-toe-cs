#! /usr/bin/env python

# Alexander Williams
# CSCE 3600.001
# Minor 5
# minor5client.py

from socket import *
from sys import *
from select import *

if len(argv) != 3: #checking if port was given
    print 'usage: python',str(argv[0]),'hostname','port'
    quit()

sockfd = socket(AF_INET, SOCK_STREAM) #opening socket
if sockfd < 0:
    print 'ERROR opening socket'
    quit()

portno = int(argv[2])
ip = gethostbyname(argv[1])

sockfd.connect((ip, portno)) #connecting to server
if sockfd < 0:
    print 'ERROR connecting'
    quit()

sockets = [stdin, sockfd] #socket list for select

while True:
    inputs, outputs, errors = select(sockets, [], []) #selecting socket from server or stdin
    for i in inputs:
        if i == sockfd: #reading from server
            message = i.recv(1024)
            if message: #if connected
                print message
                if message == 'You win, X resigned.\n' or message == 'You win, O resigned.\n' or message == 'You win\n' or message == 'You lose\n' or message == 'Tie game\n':
                    sockfd.close()
                    quit()
            else: #if disconnected
                quit()
            message = None
        else: #reading from stdin
            message = raw_input()
            if message:
                sockfd.send(message)
                if message == 'R': #quitting if resigned
                    sockfd.close()
                    quit()
            message = None

sockfd.close()
