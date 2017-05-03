import os

class File(): 
    def __init__(self,file_id,name,url,parent):
        self.id = file_id
        self.name = name
        self.url = url
        self.parent = parent
        self.path = None
        self.timestamp = None
        self.size = None
        self.sync = False
        

    def download(self,session):
        r = requests.get(url, stream=True)
        path = "{0}/{1}".format(self.path,self.name)
        if not(os.path.exists(self.path)):
            os.makedirs(self.path)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        self.sync = True

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name