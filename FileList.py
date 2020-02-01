import os

class FileList(object):
    _instance=None

    
    fileList=[
        
    ]

    def getList(self):
        return self.fileList

    def addFile(self,fileObj):
        self.fileList.append(fileObj)

    def deleteFile(self,id):
        for item in self.fileList[:]:  
            if int(item["id"]) == int(id):
                if os.path.exists(item['filePath']):
                    os.remove(item['filePath'])
                    self.fileList.remove(item)
                    return True
                else :
                    return False
        return False
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            obj = object.__new__(cls)
            cls._instance = obj
        return cls._instance

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(FileList, "_instance"):
            with FileList._instance_lock:
                if not hasattr(FileList, "_instance"):
                    FileList._instance = FileList(*args, **kwargs)
        return FileList._instance
    