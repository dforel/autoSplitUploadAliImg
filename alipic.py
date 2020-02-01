#!/usr/bin/python3
# -*- coding: UTF-8 -*-
 
import requests, os, sys, time
from urllib3 import encode_multipart_formdata
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
from util import getCurrentTime

class UploadWrap(object):
    _instance=None
 
    taskMap={
        "id":None
    }

    def startWork(self, inputM3u8, tempFilePath):
        
        id=getCurrentTime() 
        (fileName,extension) = os.path.splitext(inputM3u8)
        uploadTask = SplitToolMan(inputM3u8,fileName+"_out.m3u8",tempFilePath) # keepprint will print out one line every 2 seconds
        uploadTask.runBackground()
        self.taskMap.update({id: uploadTask}) 
        return id
    
    def get_status(self, id):
        print(self.taskMap)
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].getStatus()
        return False,"未找到"
    def get_log(self, id):
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].getResultLog()
        return False,"未找到"
    def get_m3u8(self, id):
        if(self.taskMap.__contains__(id)): 
            return True,self.taskMap[id].getOutputM3u8()
        return False,"未找到"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            obj = object.__new__(cls)
            cls._instance = obj
        return cls._instance

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(UploadWrap, "_instance"):
            with UploadWrap._instance_lock:
                if not hasattr(UploadWrap, "_instance"):
                    SplitFatory._instance = UploadWrap(*args, **kwargs)
        return UploadWrap._instance

class SplitToolMan:
    """帮忙切割上传的工具人"""
    total = 0
    current=0
    error_retry=0
    timeout=0
    inputM3u8=""
    outputM3u8=""
    tempFilePath=""
    resultLog=[]
    status="UNSTART" # RUNNING  FINISHED

    url = 'https://kfupload.alibaba.com/mupload'
    headers = {'user-agent':'iAliexpress/6.22.1 (iPhone; iOS 12.1.2; Scale/2.00)', 'Accept':'application/json', 'Accept-Encoding':'gzip,deflate,sdch', 'Connection':'close'}
    def __init__(self, inputM3u8, outputM3u8, tempFilePath='./', error_retry=10, timeout=40):
        self.inputM3u8=inputM3u8
        self.outputM3u8=outputM3u8
        self.tempFilePath=tempFilePath
        self.error_retry=error_retry
        self.timeout=timeout
    def m_upload(self,filename):
        fakename = os.path.splitext(filename)[0] + '.jpg'
        payload = {'scene':'aeMessageCenterV2ImageRule', 'name':fakename, 'file': (fakename,open(self.tempFilePath+'/'+filename,'rb').read())}
        encode_data = encode_multipart_formdata(payload)
        data = encode_data[0]
        self.headers['Content-Type'] = encode_data[1]
        self.current = self.current + 1
        for _ in range(self.error_retry):
            try:
                r = requests.post(self.url, headers=self.headers, data=data, timeout = self.timeout) 
                self.appendLog(r.text) 
                if r and 'url' in r.text:
                    #print(filename + " upload")
                    #print(r.json()['url']) 
                    self.appendLog("total:{0},current:{1}".format(self.total,self.current));
                    return r.json()['url']
                else:
                    #失败的时候等待1秒重试
                    time.sleep(1)
                    raise Exception('upload filename:{1} error'.format(filename))
            except:
                self.appendLog('Failed to upload ' + filename + '\n')
                continue
        self.appendLog("total:{0},current:{1}".format(self.total,self.current));
        return filename + ''

    def appendLog(self, log):
        self.resultLog.append(log)

    def getStatus(self):
        return self.status

    def getResultLog(self):
        return self.resultLog

    def getOutputM3u8(self):
        return self.outputM3u8

    def startWork(self):
        self.status = "RUNNING"
        m3u8 = open(self.inputM3u8)
        new_m3u8 = open(self.outputM3u8, 'w')
        file_upload = {t.strip():'' for t in m3u8.readlines() if t[0]!='#' and t.find("http")<0}
        m3u8.seek(0)
        # 如果有失败的，可以调节下方的workers数量，减少一些试试看
        #print(file_upload); 
        self.total = len(file_upload)
        self.current = 0; 
        executor = ThreadPoolExecutor(max_workers=4)
        futures = {executor.submit(self.m_upload, filename):filename for filename in file_upload.keys()}
        for future in as_completed(futures):
            file_upload[futures[future]] = future.result()
        
        for line in m3u8:
            if line[0] != '#' and line.find("http")<0:
                new_m3u8.write(file_upload[line.strip()] + '\n')
            else:
                new_m3u8.write(line) 
        self.status = "FINISHED"
        self.appendLog("Complete") 
    
    def runBackground(self):
        t1 = Thread(target=self.startWork)
        t1.start() 

if __name__ == '__main__': 
    
    toolMan=SplitToolMan(sys.argv[1],sys.argv[2],sys.argv[2])
    toolMan.startWork() 
    #print("Complete")