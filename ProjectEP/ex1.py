import os
import time

def get_cpu_load():
    """ Returns a list CPU Loads"""
    result = []
    cmd = 'typeperf "\Processor(_Total)\% Processor Time'
    response = os.popen(cmd,'r').read().strip().split("\r\n")
    print response
    #for load in response[1:]:
     #  result.append(int(load))
    return result

if __name__ == '__main__':
    time.sleep(5)
    print get_cpu_load()