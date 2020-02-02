# -*- coding: UTF-8 -*-

import subprocess, time
from util import getCurrentTime
from threading import Thread
import tempfile

class SplitFatory(object):
    _instance=None
 
    taskMap={
        "id":None
    }

    def execShell(self, cmd,m3u8):
        keepprinting = Shell(cmd,m3u8) # keepprint will print out one line every 2 seconds
        keepprinting.run_background()
        id=getCurrentTime()
        self.taskMap.update({id: keepprinting})
        # keepprinting.print_output()
        return id
    def get_status(self, id):
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].get_status()
        return False,"未找到"
    def get_log(self, id):
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].getLog()
        return False,"未找到"
    def get_m3u8(self, id):
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].get_m3u8()
        return False,"未找到"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            obj = object.__new__(cls)
            cls._instance = obj
        return cls._instance

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SplitFatory, "_instance"):
            with SplitFatory._instance_lock:
                if not hasattr(SplitFatory, "_instance"):
                    SplitFatory._instance = SplitFatory(*args, **kwargs)
        return SplitFatory._instance

class Shell(object):
    def __init__(self, cmd,m3u8):
        self.cmd = cmd
        self.ret_code = None
        self.ret_info = None
        self.err_info = None
        self.m3u8 = m3u8
        self.out_temp = tempfile.TemporaryFile(mode='w+')
        self.logRecord= []
        self.run_time = 0
 
    def run_background(self): 
        # 获取临时文件的文件号
        fileno = self.out_temp.fileno()
        self._process = subprocess.Popen(self.cmd, stdout=fileno, stderr=fileno, shell=True)
        t1 = Thread(target=self.saveLog)
        t1.start() 

    def get_m3u8(self):
        return self.m3u8
 
    def get_status(self):
        retcode = self._process.poll()
        if retcode == None:
            status = "RUNNING" 
        else:
            status = "FINISHED"
        return status

    # 停止进程
    def stop(self):
        # 停止子进程
        self.sub_proc.terminate()
        self.proc.terminate()
        # 结果存进文件
        self.get_result()
 
    def saveLog(self):
        while True:
            time.sleep(1)
            print("==========================================")
            self.run_time=self.run_time+1
            
            print(self.run_time)
             # 从临时文件读出shell命令的输出结果
            self.out_temp.seek(0)
            rt = self.out_temp.read()
    
            # 以换行符拆分数据，并去掉换行符号存入列表
            self.logRecord = rt.strip().split('\n') 
            # print(self.logRecord)
            # print(line)
            # print(self.get_status())
            print("==========================================") 
            if self.get_status()=="FINISHED":
                # 保存日志一个小时，然后清空日志。
                time.sleep(60*60)
                self.logRecord=[]
                break 
    def getLog(self):
        return self.logRecord
 
# keepprinting = Shell("/tmp/keepprint") # keepprint will print out one line every 2 seconds
# keepprinting.run_background()
# keepprinting.print_output()