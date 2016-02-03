import win32process
import win32api
import win32con
import win32gui
import time
from PIL import ImageGrab
import os

def CheckifProcess(procname):
    processes = win32process.EnumProcesses()
    ifopen =False
    iffront=False
    ans=False
    data = ""
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
            if proc[i]["Process id"]==procid_first:
                iffront=True
        else:
            i+=1
    if(ifopen==True and iffront==True):
        ans=True
    return ans



def PrintScreen(i):
    im = ImageGrab.grab()
    picname="pic"+str(i)+".png"
    im.save(picname)
    print "Took Screenshot | Saved as : ",picname

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
    while proc[i]["Process name"]==procname:
        ans=True
        if proc[i]["Process id"]!=procid_first:
            pass
        else:
            check=CheckifProcess(proc[i]["Process name"])
            while(check==True):
                PrintScreen(t)
                t+=1
                time.sleep(2)
                check=CheckifProcess(proc[i]["Process name"])
    else :
        i+=1

if (ans == False):
    print procname,"isn't running"






