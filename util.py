import time
def getCurrentTime():
    now = int(time.time())     # 1533952277
    timeArray = time.localtime(now) 
    otherStyleTime = time.strftime("%Y%m%d%H%M%S", timeArray)
    return otherStyleTime