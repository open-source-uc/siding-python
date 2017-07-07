
class Organization():
  def __init__(self,courses,siding):
    self.acronym = courses[0].acronym
    self.name = courses[0].name
    self.courses = courses
    self.folders = self.get_folders()
    self.forms = self.get_forms()
    print(self.forms)
    self.siding = siding
    
    print(self.folders)

  def get_folders(self):
    folders = {}
    for course in self.courses:
      for folder in course.folders.values():
        if not(folder.name in folders):
          folders[folder.name] = []
        folders[folder.name].append(folder)
    folders = {k:v for k,v in folders.items() if len(v) == len(self.courses)}
    return folders
  
  def get_forms(self):
    forms = {}
    for course in self.courses:
      print(course.forms)
      for form_name,form_id in course.forms.items():
        if not(form_name in forms):
          forms[form_name] = []
        forms[form_name].append(form_id)
    forms = {k:v for k,v in forms.items() if len(v) == len(self.courses)}
    return forms

  
  def new_form(self,name,start_date,start_time,end_date,end_time,resend='SI'):
    new_form = self.siding.new_form    
    attemps = []
    forms_ids = []
    for course in self.courses:
      resp, form_id = new_form(course.course_id,name,start_date,start_time,end_date,end_time)
      attemps.append(resp.status_code)
      forms_ids.append(form_id)
    return attemps,forms_ids
    
  def delete_form(self,form_name):
    del_form = self.siding.delete_form
    forms = self.forms[form_name]   
    attemps = []
    for course,form_id in zip(self.courses,forms):
      resp = del_form(course.course_id,form_id)
      attemps.append(resp.status_code)
    return attemps

  def add_question(self,forms_id,question):
    pass
  
  def new_notice(self,):
    pass
  
  def create_folder(self,folder_name):
    folders = folder_name.split("/")    
    if not(self.folders[folder_name]):
      
      pass
    pass

  def upload_file(self,folder, desc, ffile, filepath=None, pos=2, vis='si'):
    upload = self.siding.upload_file
    folders = self.folders[folder]
    attemps = []
    for course,folder in zip(self.courses,folders):
      res = upload(course.course_id,folder.folder_id,desc,ffile,filepath,pos,vis)
      attemps.append((res,res.status_code))
    return attemps

  def delete_file(self,fname):
    delete = self.siding.delete_file
    attemps = []
    for course in self.courses: 
      file_ = list(filter(lambda x: x.name == fname,course.files.values()))[0]
      folder = file_.parent.folder_id
      file_id = file_.id
      res = delete(course.course_id,folder,file_id)
      attemps.append((res,res.status_code))
    return attemps

  def retry(self,func,*args):
    pass