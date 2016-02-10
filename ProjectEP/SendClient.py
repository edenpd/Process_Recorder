import socket               # Import socket module
import os


PORT = 12345                 # Reserve a port for your service.
BUF_SIZE = 1024

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
s.connect((host, PORT))
f = open('E:\Python Yud Bet\ProjectEP\PICS\pic2.png','rb')
print 'Sending...'
part = f.read()
while (part):
    s.send(part)
    part = f.read(BUF_SIZE)
s.send(part)
f.close()
print "Image sent"
s.shutdown(socket.SHUT_WR)
print s.recv(BUF_SIZE)
s.close()

