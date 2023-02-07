import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# AF : address family
# AF_INET : designates the types of addresses our socket can communicate with
# In this case, IPv4 addresses
# SOCK_STREAM means a TCP socket
# SOCK_DGRAM means a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server_socket.setsockopt(socket.SQL_SOCKET, socket.SO_REUSEADDR , 1)

#binding our server socket to an IP address and PORT number
server_socket.bind((IP,PORT))

#server socket listening for any requests
server_socket.listen()

#list of all the sockets (server socket + client sockets)
sockets_list = [server_socket]

#map
#client socket as key, and the user data as the value(username header, username)
clients = {}

#function to receive a message from the client
def receive_message(client_socket):
    try:
        #First we receive only the data equal to the HEADER_LENGTH.
        #It will only include the length of the message (or username)
        message_header = client_socket.recv(HEADER_LENGTH)

        #If we didn't receive any data, the client closed the connection
        if (len(message_header)==0):
            return False

        #strip() method removes all the spaces.
        #Although, Python can handle it without the strip method too.
        message_length = int(message_header.decode("utf-8").strip())

        #return message header and the message 
        #Here, in the "data", we receive the next left data, which will be the username or the message
        return {"header" : message_header, "data": client_socket.recv(message_length)}
    except:
        return False


#always listen for requests
while True:

    #The select() call monitors activity on a set of sockets looking for sockets
    # ready for reading, writing, or with an exception condition pending.

    #select.select() method takes in 3 params:
    #read list (The sockets we wanna read),
    #write list (The sockets we wanna write),
    #exceptional error sockets
    read_sockets, _, exception_sockets = select.select(sockets_list, [] , sockets_list)

    for notified_socket in read_sockets:
        #someone just connected to the server
        if notified_socket == server_socket:
            
            client_socket, client_address = server_socket.accept()
            
            #When a client socket connects to the server for the first time,
            #the client sends the username of the user.

            #Hence, the user will contain the header, and the username returned from the function
            user = receive_message(client_socket)

            if user is False:
                continue

            #client_socket added to the sockets list
            sockets_list.append(client_socket)

            #mapping the dictionary data to the client socket key
            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")


        else:
            # If the connection by client is not for the first time,
            # then a message has been sent by the client (instead of username)
            # Hence, the message variable contains the message header and the message data
            message = receive_message(notified_socket)

            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            
            #get user data from the clients map
            user = clients[notified_socket]

          
            print(f"Received message from {user['data'].decode('utf-8')} : {message['data'].decode('utf-8')}")

            #Send the message received from a client to all other clients
            # for client_socket in clients:
            #     if client_socket != notified_socket:
            #         client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])


    # Delete all the sockets which created errors
    for notified_sockets in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

