#! /usr/bin/env python

# Alexander Williams
# CSCE 3600.001
# Minor 5
# minor5server.py

from socket import *
from sys import *
from select import *

############
#FUNCTIONS:#
############

#CREATE BOARD TEXT FUNCTION
def createBoardText(b):
    boardtext = "\n  board\n  1 2 3\n +-+-+-+\nA|"
    for row in range(len(b)):
        for col in range(len(b[row])):
            boardtext += b[row][col] + "|"
        boardtext += "\n +-+-+-+\n"
        if row == 0:
            boardtext += "B|"
        if row == 1:
            boardtext += "C|"
    return boardtext

#PRINT BOARD FUNCTION
def printBoard(b):
    for x in range(3):
        for y in range(3):
            print b[x][y],
        print

#MESSAGE CHECK FUNCTION
def messageCheck(m):
    #returns 0 on invalid command, 1 on valid command and move, and 2 on invalid move
    if m[0] != 'M':
        return 0
    if m[1] != 'A' and m[1] != 'B' and m[1] != 'C':
        return 2
    if not m[2].isdigit() or int(m[2]) > 3 or int(m[2]) < 1:
        return 2
    return 1

#SPOT CHECK FUNCTION
def spotCheck(row, col, b):
    if b[row][col] == ' ':
        return True
    return False

#TIE CHECK FUNCTION
def tieCheck(b):
    for row in range(len(b)):
        for col in range(len(b[row])):
            if b[row][col] == ' ':
                return False
    return True

#WIN CHECK FUNCTION
def winCheck(b, letter):
    diawin = 0
    diawin2 = 0
    for row in range(len(b)):
        count = 0
        for col in range(len(b[row])): #row wins
            if b[row][col] != letter:
                break;
            count = count + 1
            if count == 3:
                return True
        count = 0
        for col in range(len(b[row])): #col wins
            if b[col][row] != letter:
                break
            count = count + 1
            if count == 3:
                return True
        for col in range(len(b[row])): #top left bottom right win
            if row == col:
                if b[row][col] != letter:
                    break
                diawin = diawin + 1
                if diawin == 3:
                    return True
        for col in range(len(b[row])): #bottom left top right win
            if row == 2 and col == 0 or row == 1 and col == 1 or row == 0 and col == 2:
                if b[row][col] != letter:
                    break
                diawin2 = diawin2 + 1
                if diawin2 == 3:
                    return True
    return False

#############

#############
#MAIN SCRIPT#
#############

if len(argv) != 2: #checking if port was given
    print 'usage: python',  str(argv[0]), 'port'
    quit()

board = [[' ']*3,[' ']*3,[' ']*3] #creating board

sockfd = socket(AF_INET, SOCK_STREAM) #opening socket
if sockfd < 0:
    print 'ERROR opening socket'
    quit()

portno = int(argv[1])

sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #reuse address

sockfd.bind(("", int(argv[1]))) #binding socket
sockfd.listen(5); #listening for connections

print 'Waiting on Clients'

newsockfd, (remotehost, remoteport) = sockfd.accept() #accepting first socket
if newsockfd < 0:
    print 'ERROR on accept #1'
    quit()

print 'X< Connected'
print 'X> You are player X. Waiting on player O to connect.'
newsockfd.send("You are player X. Waiting on player O to connect.")

newsockfd2, (remotehost2, remoteport2) = sockfd.accept() #accepting second socket
if newsockfd2 < 0:
    print 'ERROR on accept #2'
    quit()

print 'O< Connected'
print 'O> You are player O.'
newsockfd2.send("You are player O.")

print 'X> ' #sending initial messages with board
print createBoardText(board)
print 'X> Your turn'
print 'O> '
print createBoardText(board)
newsockfd.send(createBoardText(board) + 'Your turn\n')
newsockfd2.send(createBoardText(board))

sockets = [newsockfd, newsockfd2] #input sockets list for select

turn = 0 #var for who's turn it is
while True:
    inputs, outputs, errors = select(sockets, [], []) #selecting socket to read
    for i in inputs:
        message = i.recv(1024)
        if not message and i == newsockfd: #if player 1 left
            print 'X< Disconnected'
            print 'O> You win, X resigned.'
            newsockfd2.send('You win, X resigned.\n')
            newsockfd.close()
            newsockfd2.close()
            quit()
        elif not message and i == newsockfd2: #if player 2 left
            print 'O< Disconnected'
            print 'X> You win, O resigned.'
            newsockfd.send('You win, O resigned.\n')
            newsockfd.close()
            newsockfd2.close()
            quit()
        else:
            if i == newsockfd:
                if message == "R": #if player 2 resigned or left
                    newsockfd2.send('You win, X resigned.\n')
                    print 'O> You win, X resigned.'
                    newsockfd.close()
                    newsockfd2.close()
                    quit()
                elif message == '?': #if player 1 asks for help
                    newsockfd.send('?-Display this help\nR-Resign\nM<R><C>-Move where <R> is a row A, B, or C and <C> is a column 1, 2, or 3\n\tExample Moves: MA1 MC3, MB1\n')
                    print 'O> ?-Display this help\nR-Resign\nM<R><C>-Move where <R> is a row A, B, or C and <C> is a column 1, 2, or 3\n\tExample Moves: MA1 MC3, MB1'
                elif turn == 0 and messageCheck(message) == 1 and spotCheck(ord(message[1]) - 65, ord(message[2]) - 49, board): #valid command and valid turn
                    row = ord(message[1]) - 65
                    col = ord(message[2]) - 49
                    board[row][col] = 'X'
                    printBoard(board)
                    newsockfd.send(createBoardText(board))
                    print 'X>', createBoardText(board)
                    newsockfd2.send(createBoardText(board))
                    print 'O>', createBoardText(board)
                    if not winCheck(board, 'X') and not winCheck(board, 'O') and not tieCheck(board):
                        newsockfd2.send('Your turn\n')
                        print 'O> Your turn'
                        turn = 1
                elif turn == 0 and messageCheck(message) == 1 and not spotCheck(ord(message[1]) - 65, ord(message[2]) - 49, board): #spot was taken
                        newsockfd.send('That spot is already taken\n')
                        print 'X> That spot is already taken'
                elif turn == 0 and messageCheck(message) == 2:
                    newsockfd.send('Invalid move\n   Move should be M<R><C> with no spaces\n   Example: MA1 or MB3\n')
                    print 'X> Invalid move   Move should be M<R><C> with no spaces\n   Example: MA1 or MB3\n'
                elif turn == 0: #invalid commmand
                    newsockfd.send('Invalid command\n')
                    print 'X> Invalid command'
                else: #not their turn
                    newsockfd.send("Not your turn")
            else:
                if message == 'R': #if player 1 resigned or left
                    newsockfd.send('You win, O resigned.\n')
                    print 'X> You win, O resigned.'
                    newsockfd.close()
                    newsockfd2.close()
                    quit()
                elif message == '?': #if player 2 asks for help
                        newsockfd2.send('?-Display this help\nR-Resign\nM<R><C>-Move where <R> is a row A, B, or C and <C> is a column 1, 2, or 3\n\tExample Moves: MA1 MC3, MB1\n')
                        print 'O> ?-Display this help\nR-Resign\nM<R><C>-Move where <R> is a row A, B, or C and <C> is a column 1, 2, or 3\n\tExample Moves: MA1 MC3, MB1'
                elif turn == 1 and messageCheck(message) == 1 and spotCheck(ord(message[1]) - 65, ord(message[2]) - 49, board): #valid command and valid turn
                    board[ord(message[1]) - 65][ord(message[2]) - 49] = 'O'
                    newsockfd2.send(createBoardText(board))
                    print 'O>', createBoardText(board)
                    newsockfd.send(createBoardText(board))
                    print 'X>', createBoardText(board)
                    if not winCheck(board, 'X') and not winCheck(board, 'O') and not tieCheck(board):
                        newsockfd.send('Your turn\n')
                        print 'X> Your turn'
                        turn = 0
                elif turn == 1 and messageCheck(message) == 1 and not spotCheck(ord(message[1]) - 65, ord(message[2]) - 49, board): #spot was taken
                    newsockfd2.send('That spot is already taken\n')
                    print 'O> That spot is already taken'
                elif turn == 1 and messageCheck(message) == 2:
                    newsockfd2.send('Invalid move\n   Move should be M<R><C> with no spaces\n   Example: MA1 or MB3\n')
                    print 'O> Invalid move\n   Move should be M<R><C> with no spaces\n   Example: MA1 or MB3\n'
                elif turn == 1: #invalid commmand
                    newsockfd2.send('Invalid command\n')
                    print 'O> Invalid command'
                else: #not their turn
                    newsockfd2.send("Not your turn")
            if winCheck(board, 'X'): #checking if 'X' won
                newsockfd.send('You win\n')
                newsockfd2.send('You lose\n')
                print 'X> You win\nO> You lose\n'
                newsockfd.close()
                newsockfd2.close()
                quit()
            if winCheck(board, 'O'): #checking if 'O' won
                newsockfd2.send('You win\n')
                newsockfd.send('You lose\n')
                print 'O> You win\nX> You lose'
                newsockfd.close()
                newsockfd2.close()
                quit()
            if tieCheck(board): #checking if tie game
                newsockfd.send('Tie game\n')
                newsockfd2.send('Tie game\n')
                print 'X> Tie game\nO> Tie game'
                newsockfd.close()
                newsockfd2.close()
                quit()

newsockfd.close()
newsockfd2.close()
