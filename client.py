import socket
import select
import errno

HEADER_LENGTH = 10

IP = '127.0.0.1'
PORT = 1234

#Ask the client for a username
my_username = input("Username: ")

#IPv4 address family, TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connecting the client socket to the server socket
client_socket.connect((IP,PORT))

#socket object set to non blocking mode
client_socket.setblocking(False)

username = my_username.encode("utf-8")

#username_header will be the length of the username.
#The length of the username_header will be equal to the HEADER_LENGTH
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")

#send the username header and the username to the server socket
client_socket.send(username_header + username)


while True:
    #input message
    message = input(f"{my_username} > ")

    #handling if the user did input a message
    if message:
        message = message.encode("utf-8")
        message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")

        #send the message header and message to the server socket
        client_socket.send(message_header + message)

    try:
        while True:
            #receive things from the server socket
            username_header = client_socket.recv(HEADER_LENGTH)

            if not len(username_header):
                print("Connection closed by the server")
                SystemExit()

            #username data of the person who sent the message
            username_length = int(username_header.decode("utf-8").strip())
            username = client_socket.recv(username_length).decode("utf-8")
            
            #message data sent by the server socket
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode("utf-8").strip())
            message = client_socket.recv(message_length).decode("utf-8")

            print(f"{username} > {message}")

    #IOError is Input/Output error
    except IOError as e:
        # EAGAIN is often raised when performing non-blocking I/O.
        # It means "there is no data available right now, try again later".

        # EWOULDBLOCK: In non-blocking mode, if a recv() call doesn’t find any data,
        # or if a send() call can’t immediately dispose of the data, a error exception is raised.
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error ', str(e))
            SystemExit()

    #handling any exception
    except Exception as e:
        print('General error ',str(e))
        SystemExit()