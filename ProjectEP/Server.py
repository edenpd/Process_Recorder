###############################
#########  IMPORTS  ###########
###############################
import sys
import errno
import socket
import threading
import os
import struct
import time
###############################
########  VARIABLES  ##########
###############################
IP = "0.0.0.0"
PORT = 8085
ADDRESS = (IP, PORT)
BACKLOG = 5
BLOCKING = 0
BUF_SIZE = 4096
clients = []
###############################
#########  CLASSES  ###########
###############################
class Client(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.socket = socket
        (ip, port) = address
        self.name = "Client-%s:%d" % (ip, port)
        self.address = address

    def shutdown(self):
        self.connected = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print "%s has disconnected" % (self.name)
        clients.remove(self)

    def recieve_picture(self):
        len_data = self.socket.recv(100)
        print '------------', len_data

        self.socket.send( "startsendfile")
        pic = self.socket.recv(BUF_SIZE)
        buffer_data = ""
        '''
        len_part = 0
        while len_part < int(len_data):
            pic = self.socket.recv(BUF_SIZE)
            if len(pic) == BUF_SIZE:
                len_part += BUF_SIZE
            else:
                len_part += len(pic)
            buffer_data += pic
        '''
        print "endsendfile"
        self.socket.send( "endsendfile" )
        return buffer_data

    def run(self):
        self.connected = True
        while self.connected:
            with threading.Lock():
                try:
                        output = self.recieve_picture()
                        print "this is the output :       ",len(output)
                        time.sleep(1)
                        path= os.path.dirname(os.path.abspath(__file__))
                        path +="\\PICS"
                        if(os.path.isdir(path)==False):
                            os.makedirs(path)
                        with open(path+"\\pic1.jpg", "wb") as f:
                            f.write(output)
                except socket.error as error:
                    if error.errno != 10035:
                        print "Error", error.errno
                    if error.errno == errno.WSAEWOULDBLOCK:
                        # A non-blocking socket operation could not be completed immediately
                        continue
                    elif error.errno == errno.WSAECONNRESET:
                        # An existing connection was forcibly closed by the remote host
                        self.shutdown()
                        continue
                    elif error.errno == errno.EBADF:
                        # Bad file descriptor
                        continue
                    else:
                        raise error
## ------------------------- ##
class Server(object):
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.server.setblocking(BLOCKING)
        self.server.bind(ADDRESS)
        self.server.listen(BACKLOG)

    def shutdown(self):
        for client in clients:
            client.socket.send("Server shutting down")
            client.connected = False
            client.socket.close()
            client.join()
        self.server.close()

    def run(self):
        self.running = True
        while self.running:
            try:
                (client_socket, client_address) = self.server.accept()
                (ip, port) = client_address
                print "Client-%s:%d has connected" % (ip, port)
                client = Client(client_socket, client_address)
                clients.append(client)
                client.start()
                procname=raw_input("Enter the process name : ")
                procname=procname+".exe"
                client.socket.send(procname)
            except socket.error as error:
                if error.errno == errno.WSAEWOULDBLOCK:
                    # A non-blocking socket operation could not be completed immediately
                    continue
                elif error.errno == errno.WSAECONNRESET:
                    # An existing connection was forcibly closed by the remote host
                    self.running = False
                    self.shutdown()
                    continue
                else:
                    raise error

    def __enter__(self):
        return self

    def __exit__ (self, type, value, traceback):
        self.shutdown()
###############################
########  FUNCTIONS  ##########
###############################
def main(argv=[]):
    with Server() as server:
        server.run()
###############################
###########  MAIN  ############
###############################
if __name__ == "__main__":
    main(sys.argv[1: ])
###############################
###########  QUIT  ############
###############################