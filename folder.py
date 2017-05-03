class Folder():
  def __init__(self,folder_id,name,url,parent):
    self.folder_name = name
    self.folder_id = folder_id
    self.url = url
    self.parent = parent 
    self.files = {}

  def __str__(self):
    return self.folder_name
  def __repr__(self):
    return self.folder_name
    
  def path(self):
    return this.parent.path + "/"+ self.name