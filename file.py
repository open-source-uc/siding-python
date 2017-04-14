import os

class File(): 
    def __init__(self):
        self.url = None
        self.path = None
        self.filename = None
        self.sync = False
        self.timestamp = None
        self.size = None

    def download(self,session):
        r = requests.get(url, stream=True)
        path = "{0}/{1}".format(self.path,self.filename)
        if not(os.path.exists(self.path)):
            os.makedirs(self.path)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        self.sync = True

    def func2(self):
        pass