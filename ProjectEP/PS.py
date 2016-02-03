#region ------------------------ IMPORTS ------------------------
import win32process
import win32api
import win32con
import win32gui
import time
from PIL import ImageGrab
import os
#endregion

#region ------------------------ METHODS ------------------------
def CheckifProcess(procname):
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

def PrintScreen(i):
    path= os.path.dirname(os.path.abspath(__file__))
    path=path+"\PICS"
    if(os.path.isdir(path)==False):
        os.makedirs(path)
    im = ImageGrab.grab()
    picname="pic"+str(i)+".png"
    im.save(path+"\{0}".format(picname))
    print "Took Screenshot | Saved as : ",picname
#endregion

#region -------------------------- MAIN -------------------------
ans=False
procname=raw_input("Enter the process name : ")
procname=procname+".exe"
time.sleep(5)


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
            check=CheckifProcess(proc[i]["Process name"])
            if check["if front"]==False and printf==False:
                print procname, "was minimized or closed... please wait..."              #waiting that process will come to front - minimized or closed
                printf=True
            while(check["if open"]==True and check["if front"]==True):
                printf=False
                PrintScreen(t)
                t+=1
                time.sleep(2)
                check=CheckifProcess(proc[i]["Process name"])
            """if(check["if open"]==False):
                print procname, "was closed"
                break"""                                                       #close program when process closed
    else :
        i+=1

if (ans == False):
    print procname,"isn't running"
#endregion

