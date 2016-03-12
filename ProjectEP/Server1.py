###############################
#######  INFORMATION  #########
###############################
## Authors:                  ##
## Eden Podoksik             ##
## Platform: Windows 7 64bit ##
## Version: Python 2.7       ##
## ------------------------- ##
## Python communication      ##
## Server                    ##
###############################

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
import pickle, zlib
from PIL import  Image

###############################
########  VARIABLES  ##########
###############################
IP = "0.0.0.0"
PORT = 8085
Broadcast_PORT = 8084
Broadcast_IP ="255.255.255.255"
ADDRESS = (IP, PORT)
BACKLOG = 5
BLOCKING = 1
BUF_SIZE = 1024
clients = []
guisocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###############################
#########  CLASSES  ###########
###############################
class Broadcast(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.broadsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadsocket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)


    def run(self):
        while True:
            self.broadsocket.sendto("Connect to me", (Broadcast_IP, Broadcast_PORT))



class Client(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.socket = socket
        (ip, port) = address
        self.address=address
        self.name = "Client-%s:%d" % (ip, port)
        self.address = address

    #------------------------------------------------------------------------------------------------------------------

    def shutdown(self):
        self.connected = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print "%s has disconnected" % (self.name)
        guisocket.send("disconnected"+"$"+self.address[0]+"#"+str(self.address[1]))
        clients.remove(self)

    #------------------------------------------------------------------------------------------------------------------

    def recieve_picture(self):
        len_image=self.socket.recv(BUF_SIZE)
        size = int(len_image)
        self.socket.send("ack")
        buffer_data = ""
        len_part = 0
        while len_part < size:
            pic = self.socket.recv(2048)
            if len(pic) == 2048:
                len_part += 2048
            else:
                len_part += len(pic)
            buffer_data += pic

        print "got the picture!"
        self.socket.send("ack")

        compressed = pickle.loads(buffer_data)
        picture = zlib.decompress(compressed)
        picture = eval(picture)
        im = Image.fromstring(picture['mode'], picture['size'], picture['pixels'])
        picname=self.socket.recv(BUF_SIZE)
        server_path= os.path.dirname(os.path.abspath(__file__))
        server_path+="\SERVER_PICS"+"\{0}".format(picname)
        print "This is the path: ",server_path
        im.save(server_path)
        guisocket.send("image_sent#"+server_path)
    #-------------------------------------------------------------------------------------------------------------------

    def Data_Collection(self):
        detailes=guisocket.recv(BUF_SIZE)
        detailes=detailes.split("$")
        IP=detailes[0]
        Port=detailes[1]
        Exceptions=detailes[2]
        Time=detailes[3]*60

        self.socket.send(Time)
        time.sleep(0.1)
        self.socket.send(Exceptions)

        FoundExcpretions=self.socket.recv(BUF_SIZE)
        FoundExcpretions=FoundExcpretions.split("#")

        arr=["wmp", "youtube", "cpu", "process"]
        results=""
        for i in FoundExcpretions:
            for exc in arr:
                if exc in i:
                    results+=i+"$"

        guisocket.send(results)

    #-------------------------------------------------------------------------------------------------------------------

    def run(self):
        self.connected = True
        while self.connected:
            with threading.Lock():
                try:
                    self.Data_Collection()

                    data=guisocket.recv(BUF_SIZE)
                    data+=".exe"
                    self.socket.send(data)
                    self.recieve_picture()
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

    #------------------------------------------------------------------------------------------------------------------

class Server(object):
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.server.setblocking(BLOCKING)
        self.server.bind(ADDRESS)
        self.server.listen(BACKLOG)

    #------------------------------------------------------------------------------------------------------------------

    def shutdown(self):
        for client in clients:
            client.socket.send("Server shutting down")
            client.connected = False
            client.socket.close()
            client.join()
        self.server.close()

    #------------------------------------------------------------------------------------------------------------------

    def run(self):
        Broadcast_Thread=Broadcast()
        Broadcast_Thread.start()
        self.running = True
        guisocket.connect(("127.0.0.1",1234))
        while self.running:
            try:

                (client_socket, client_address) = self.server.accept()
                (ip, port) = client_address
                guisocket.send("Connected#"+ip+"#"+str(port))
                print "Client-%s:%d has connected" % (ip, port)
                client = Client(client_socket, client_address)
                clients.append(client)
                client.start()
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