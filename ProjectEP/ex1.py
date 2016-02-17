import psutil
import multiprocessing

exception=False
number= multiprocessing.cpu_count()
CPU_USAGE= psutil.cpu_times_percent()[0]

if(number>2):
    if(CPU_USAGE<5 or CPU_USAGE>80):
        exception=True
else:
    if(CPU_USAGE>70):
        exception=True

print exception

