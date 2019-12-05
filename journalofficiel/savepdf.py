import os
from journalofficiel.alerts import Alert

class SavePDF:
    
    def __init__(self, dirpath, filename, content):
        self.dirpath = dirpath
        self.filename = filename
        self.content = content
        self.filepath = dirpath / filename
        
    @staticmethod
    def create_dir(dirpath):
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
            print("# New directory created", end=" ")
    
    @staticmethod
    def file_exists(filepath):
        return os.path.exists(filepath)
    
    def run(self):
        
        self.create_dir(self.dirpath)
   
        alert = Alert(self.filename)
        
        if not self.file_exists(self.filepath):
            open(self.filepath, 'wb').write(self.content)
            alert.run("success")
        else:
            alert.run("already_exists")