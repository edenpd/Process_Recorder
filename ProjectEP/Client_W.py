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
###############################
########  VARIABLES  ##########
###############################
IP = "127.0.0.1"
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
        path= os.path.dirname(os.path.abspath(__file__))
        path+="\PICS"
        if(os.path.isdir(path)==False):
            os.makedirs(path)
        im = ImageGrab.grab()
        picname="pic"+str(i)+".png"
        path=path+"\{0}".format(picname)
        im.save(path)
        print "Took Screenshot | Saved as : ",picname

    #------------------------------------------------------------------------------------------------------------------

    def send_picture(self, i):
        picname="pic"+str(i)+".png"
        path="E:\Python Yud Bet\ProjectEP\PICS"
        path=path+"\{0}".format(picname)
        print path
        server_path= os.path.dirname(os.path.abspath(__file__))
        server_path+="\SERVER_PICS"
        print server_path
        self.client.send(server_path+"\{0}".format(picname))
        time.sleep(2)
        if(os.path.isdir(server_path)==False):
            os.makedirs(server_path)
        f = open(path,'rb')
        print 'Sending...'
        time.sleep(1)
        part = f.read(1024)
        while (part):
            self.client.send(part)
            time.sleep(0.1)
            part = f.read(1024)
        f.close()
        mass=self.client.recv(1024)
        if mass=="image_sent":
            print picname,"sent"
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

    def Check_Exceptions(self, checkingtime):
        currenttime=time.time()
        currenttime+=checkingtime
        FoundChrome=False
        FoundWmplayer=False
        CPUexception=False
        FoundYoutube=False
        while(time.time()<=currenttime and FoundChrome==False and FoundWmplayer==False and CPUexception==False and FoundYoutube==False ):
            FoundChrome=self.Check_Media("chrome.exe")
            FoundWmplayer=self.Check_Media("wmplayer.exe")

            NumberOfCores= multiprocessing.cpu_count()
            CPU_USAGE= psutil.cpu_times_percent()[0]
            if(NumberOfCores>2):
                if(CPU_USAGE<5 or CPU_USAGE>80):
                    CPUexception=True
            else:
                if(CPU_USAGE>70):
                    CPUexception=True
            FoundYoutube=self.WindowTitles()

        self.client.send(str(FoundChrome))
        time.sleep(0.5)
        self.client.send(str(FoundWmplayer))
        time.sleep(0.5)
        self.client.send(str(CPUexception))
        time.sleep(0.5)
        self.client.send(str(FoundYoutube))



    #-------------------------------------------------------------------------------------------------------------------

    def Check_Media(self, proc):
        check=self.CheckifProcess(proc)
        if check["if open"]==True:
            return True
        else : return False

    #-------------------------------------------------------------------------------------------------------------------
    def send(self, t):
        i=1
        while(i<=t):
            self.send_picture(i)
            i+=1


    def run(self):
        self.running = True
        while self.running:
            try:
                checkingtime = self.client.recv(BUFFER)
                self.Check_Exceptions(int(checkingtime))

                data = self.client.recv(BUFFER)
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
                                while(check["if open"]==True and check["if front"]==True):
                                    printf=False
                                    self.PrintScreen(t)
                                    t+=1
                                    time.sleep(2)
                                    check=self.CheckifProcess(proc[i]["Process name"])
                                if(check["if open"]==False):
                                    print procname, "was closed"
                                    time.sleep(2)
                                    self.client.send("finish")
                                    time.sleep(2)
                                    num=str(t-1)
                                    self.client.send(num)
                                    time.sleep(2)
                                    self.send(t)
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
