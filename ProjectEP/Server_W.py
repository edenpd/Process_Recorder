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
###############################
########  VARIABLES  ##########
###############################
IP = "0.0.0.0"
PORT = 8085
ADDRESS = (IP, PORT)
BACKLOG = 5
BLOCKING = 1
BUF_SIZE = 1024
clients = []
guisocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###############################
#########  CLASSES  ###########
###############################
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
        server_path=self.socket.recv(BUF_SIZE)      #get server directory target path
        time.sleep(2)
        print "SERVER PATH : ",server_path
        guisocket.send(server_path)
        f = open(server_path,'wb')
        while True:
            print "Receiving..."
            part = self.socket.recv(BUF_SIZE)
            time.sleep(1)
            while (part):
                f.write(part)
                part = self.socket.recv(BUF_SIZE)
                time.sleep(0.1)
            break
            f.close()
            print "Done Receiving, image sent"
        self.socket.send("image_sent")
        guisocket.send("image_sent#"+server_path)
    #-------------------------------------------------------------------------------------------------------------------

    def Data_Collection(self):
        detiles=guisocket.recv(BUF_SIZE)
        detiles=detiles.split("$")
        IP=detiles[0]
        Port=detiles[1]
        Exceptions=detiles[2]
        Time=detiles[3]*60

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

                    procname=guisocket.recv(BUF_SIZE)
                    procname=procname+".exe"
                    self.socket.send(procname)
                    time.sleep(2)
                    con=self.socket.recv(BUF_SIZE)
                    if con=="finish":
                        #Photosnumber=self.socket.recv(BUF_SIZE)
                        #time.sleep(2)
                        #print "The number of the photos is : ",Photosnumber
                        #Photosnumber=int(Photosnumber)
                        #for x in range(1,Photosnumber+1):
                        #    print "Photo number",x
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

                #checkingtime=input("Enter the checking time (in minutes) : ")
                #client.socket.send(str(checkingtime*60))
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