###############################
#######  INFORMATION  #########
###############################
## Authors:                  ##
## Eden Podoksik             ##
## Platform: Windows 7 64bit ##
## Version: Python 2.7       ##
## ------------------------- ##
## Python communication      ##
## Client                    ##
###############################

###############################
#########  IMPORTS  ###########
###############################
import sys
import errno
import socket
import win32process
import win32api
import win32con
import win32gui
import time
from PIL import ImageGrab
import os
import psutil
import multiprocessing
import ctypes
import pickle, zlib

###############################
########  VARIABLES  ##########
###############################
IP = "127.0.0.1"
PORT = 8085
BLOCKING = 0
BUF_SIZE = 1024
Broadcast_PORT = 8084
Broadcast_IP ="0.0.0.0"
###############################
#########  CLASSES  ###########
###############################
class Client(object):
    def __init__(self):
        SERVER_IP=self.Broadcast_Listening()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_IP,PORT))
        #self.client.setblocking(BLOCKING)

    #------------------------------------------------------------------------------------------------------------------

    def Broadcast_Listening(self):
        Broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Broadcast_socket.bind((Broadcast_IP, Broadcast_PORT))
        details=Broadcast_socket.recvfrom(BUF_SIZE)
        while("Connect to me" != details[0]):
            details=Broadcast_socket.recvfrom(BUF_SIZE)
        IP=details[1][0]
        return  IP

    #------------------------------------------------------------------------------------------------------------------

    def shutdown(self):        
        self.client.close()

    #------------------------------------------------------------------------------------------------------------------

    def CheckifProcess(self, procname):                                     #Check if process running and not minimized
        ifopen =False
        iffront=False
        IOIF={"if open":False, "if front":False}
        proc=self.get_processes()
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

    def PrintScreen(self, i):
        try:
            server_path= os.path.dirname(os.path.abspath(__file__))
            picname="\pic"+str(i)+".png"
            server_path+="\SERVER_PICS"
            if(os.path.isdir(server_path)==False):
                os.makedirs(server_path)
            server_path+=picname
            picture = ImageGrab.grab()
            print "Took Screenshot number ",i
            image = {'pixels': picture.tostring(), 'size': picture.size, 'mode': picture.mode}
            compressed = zlib.compress(str(image))
            data = pickle.dumps(compressed)
            len_image = str(len(data))
            self.client.send(len_image)
            ack1 = self.client.recv(1024)
            self.client.send(data)
            ack2 = self.client.recv(1024)

            self.client.send(server_path)
        except Exception as e:
            print "ERROR"
            raise e

    #-------------------------------------------------------------------------------------------------------------------

    def WindowTitles(self):
        found=False
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        titles = []
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        for i in titles:
            if "YouTube" in i:
                found=True
        return found


    #-------------------------------------------------------------------------------------------------------------------

    def Check_Exceptions(self):
        checkingtime = self.client.recv(BUF_SIZE)
        time.sleep(0.1)
        Exceptions = self.client.recv(BUF_SIZE)
        Exceptions=Exceptions.split("#")
        currenttime=time.time()
        currenttime+=int(checkingtime)
        FoundProcess=False
        FoundWmplayer=False
        CPUexception=False
        FoundYoutube=False
        FoundExcpretions=""

        while(time.time()<=currenttime and FoundProcess==False and FoundWmplayer==False and CPUexception==False and FoundYoutube==False ):
            if Exceptions[0]=="True":
                FoundWmplayer=self.Check_Media("wmplayer.exe")


            if Exceptions[1]=="True":
                FoundYoutube=self.WindowTitles()

            if Exceptions[2]=="True":
                NumberOfCores= multiprocessing.cpu_count()
                CPU_USAGE= psutil.cpu_times_percent()[0]
                if(NumberOfCores>2):
                    if(CPU_USAGE<5 or CPU_USAGE>80):
                        CPUexception=True
                else:
                    if(CPU_USAGE>70):
                        CPUexception=True

            if Exceptions[3]=="True":
                proc_name=Exceptions[4]
                FoundProcess=self.Check_Media(proc_name+".exe")

        if Exceptions[0]=="True":
            FoundExcpretions+="wmp_"+str(FoundWmplayer)+"#"
        if Exceptions[1]=="True":
            FoundExcpretions+="youtube_"+str(FoundYoutube)+"#"
        if Exceptions[2]=="True":
            FoundExcpretions+="cpu_"+str(CPUexception)+"#"
        if Exceptions[3]=="True":
            FoundExcpretions+="process_"+str(FoundProcess)+"#"

        self.client.send(FoundExcpretions)

    #-------------------------------------------------------------------------------------------------------------------

    def Check_Media(self, proc):
        check=self.CheckifProcess(proc)
        if check["if open"]==True:
            return True
        else : return False

    #-------------------------------------------------------------------------------------------------------------------


    def run(self):
        self.running = True
        while self.running:
            try:

                self.Check_Exceptions()

                data = self.client.recv(BUF_SIZE)
                print data

                if "exe" in data:
                    ans=False
                    time.sleep(5)
                    procname=data
                    proc = self.get_processes()
                    hWindow = win32gui.GetForegroundWindow()
                    procid_first= win32process.GetWindowThreadProcessId(hWindow)[1]
                    t=1
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
                                if(check["if open"]==True and check["if front"]==True):
                                    printf=False
                                    self.PrintScreen(t)
                                    check=self.CheckifProcess(proc[i]["Process name"])
                                if(check["if open"]==False):
                                    print procname, "was closed"
                                    break
                        else :
                            i+=1
                    if (ans == False):
                        print procname,"isn't running"
                else:
                    print "Error"
            except socket.error as socketerror:
                print socketerror.errno
                if socketerror.errno == errno.WSAECONNRESET:
                    # An existing connection was forcibly closed by the remote host
                    self.running = False    
                try:
                    command = self.gui.recv(BUF_SIZE)
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
