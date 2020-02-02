# -*- coding: UTF-8 -*-

from flask import Flask, render_template,send_from_directory , request, redirect, url_for,make_response
from flask_wtf.file import FileField, FileRequired, FileAllowed
import os,time,json
from FileList import FileList
from util import getCurrentTime
from split import SplitFatory
from alipic import UploadWrap

app = Flask(__name__,static_url_path='',root_path='./')
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads') 

## 切割参数
preParam="ffmpeg -i {filePathName} -codec copy -map 0 -f segment -segment_list \"{tempPath}/{fileName}.m3u8\" -segment_time 3 \"{tempPath}/{fileName}_%d.ts\""

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/index')
def index(): 
    return render_template('index.html')

@app.route('/play')
def play():  
    return render_template('play.html')

@app.route('/getFileList')
def getFileList():
    instance = FileList()
    obj= resultData(True,"",instance.getList() )
    return obj

@app.route('/checkFile')
def checkFile():
    filePath=request.args.get("filePath")
    if os.path.exists(filePath):
        pathName=getCurrentTime()
        tempPath=os.path.join(os.path.dirname(__file__), 'temp', pathName)
        (sFilePath,sFileName) = os.path.split(filePath)
        (shotname,extension) = os.path.splitext(sFileName)
        data={
            "tempPath":tempPath,
            "preParam":preParam.format(filePathName=filePath,fileName=shotname,tempPath=tempPath)
        }
        obj= resultData(True,"", data )
    else:
        obj= resultData(False,"文件不存在", "" )
    return obj

@app.route('/deleteFile/<id>/', methods=['DELETE'])
def deleteFile(id): 
    try: 
        instance = FileList()
        isSuccess = instance.deleteFile(id)
        if isSuccess:
            resultData(True,"","") 
        return resultData(False,"删除失败","")
    except Exception as identifier:
        print(identifier)
        return resultData(False,"删除异常")

@app.route('/uploadFile', methods=['POST'])
def upload_file():
    result={
    "result":False,
    "msg":"上传失败"
    }
    if request.method == 'POST':
        files = request.files.get('mp4File')
        print(files)
        f = request.files['mp4File']
        # f.filename 
        (filepath, ext) = os.path.splitext(f.filename) 
        filename=getCurrentTime()
        path = os.path.join(os.path.dirname(__file__), 'upload')
        if not os.path.exists(path):
            os.makedirs(path) 
        upload_path = os.path.join(os.path.dirname(__file__), 'upload', filename+ext)
        f.save(upload_path)

        fileObj={
            "fileName":f.filename,
            "filePath":upload_path,
            "id":filename
        } 
        instance = FileList()
        instance.addFile(fileObj)

        result["result"] = True
        result["msg"] = "上传成功"
        result["path"] = upload_path
        return result
    return result

@app.route('/startSplit')
def startSplit():
    filePath=request.args.get("filePath")
    tempPath=request.args.get("tempPath")
    (sFilePath,sFileName) = os.path.split(filePath)
    (shotname,extension) = os.path.splitext(sFileName)
    cmd = preParam.format(filePathName=filePath,fileName=shotname,tempPath=tempPath)
    temp_m3u8="{tempPath}/{fileName}.m3u8".format(fileName=shotname,tempPath=tempPath)
    isExists=os.path.exists(tempPath) 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(tempPath) 

    instance = SplitFatory()
    workId = instance.execShell(cmd,temp_m3u8)
    return resultData(True,"",workId)

@app.route('/getSplitStatusAndLog')
def getSplitLog():
    workId=request.args.get("workId") 
    instance = SplitFatory()
    (isFind,logs) = instance.get_log(workId)
    (isFind,status) = instance.get_status(workId) 
    
    if(isFind==False):
        resultData(False,"找不到任务",None)
    return resultData(True,"",{"logs":logs,"status":status})

@app.route('/getM3u8')
def getM3u8():
    workId=request.args.get("workId") 
    instance = SplitFatory()
    (isFind,m3u8Path) = instance.get_m3u8(workId)  
    if(isFind==False):
        resultData(False,"找不到任务",None) 
    return resultData(True,"",{"m3u8":m3u8Path})

@app.route('/startUpload')
def startUpload():
    m3u8Input=request.args.get("m3u8Input")
    splitPathInput=request.args.get("splitPathInput")

    instance = UploadWrap()
    workId = instance.startWork(m3u8Input,splitPathInput)
    return resultData(True,"",workId)

@app.route('/getUploadStatusAndLog')
def getUploadStatusAndLog():
    workId=request.args.get("workId") 
    instance = UploadWrap()
    (isFind,logs) = instance.get_log(workId)
    (isFind,status) = instance.get_status(workId) 
    
    if(isFind==False):
        resultData(False,"找不到任务",None)

    return resultData(True,"",{"logs":logs,"status":status})

@app.route('/getUploadM3u8')
def getUploadM3u8():
    workId=request.args.get("workId") 
    instance = UploadWrap()
    (isFind,m3u8Path) = instance.get_m3u8(workId)  
    if(isFind==False):
        resultData(False,"找不到任务",None)
    return resultData(True,"",{"m3u8":m3u8Path})

@app.route('/downTemp')
def downTemp(): 
    fileName=request.args.get("filename")
    (isTempPath,shortName)=getTempPath(fileName)
    if isTempPath==False:
        return resultData(False,"只能下载temp文件夹里的文件","")
    upload_path = os.path.join(os.path.dirname(__file__), 'temp') 
    if os.path.isfile(fileName):
        First_Path,Second_Name=os.path.split(upload_path+"/"+shortName) 
        response = make_response(send_from_directory(First_Path, Second_Name))
        return response
    else:
        return resultData(False,"找不到文件")  
    return resultData()  
 
def getTempPath(fileName): 
    # fileName=request.args.get("filename")
    #fileName="E:\\work\\2020\\autoSplitUploadAliImg\\1temp\\20200201121415/20200201113731_out_out_out.m3u8"
    #fileName = os.path.abspath(fileName) 
    #print(fileName)
    upload_path = os.path.join(os.path.dirname(__file__), 'temp\\') 
    print(upload_path)
    if fileName:
        isHave= fileName.find(upload_path)
        if(isHave!=-1):
            ret = fileName.replace(upload_path, '', 1)
            return True,ret 
    return False,""

def resultData( result=False, msg="异常", data=""):
    resultObj={
        "result": result,
        "msg": msg,
        "data":data
    }
    return resultObj
 

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)