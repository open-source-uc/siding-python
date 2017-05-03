import re
from urls import *
from folder import Folder
from file import File
from bs4 import BeautifulSoup as bs

class Course():
    def __init__(self,url,link):
        self.course_id = self.get_param(link,'id_curso_ic')
        self.acronym = link.text.split()[0]
        self.name = link.text
        self.url = "{0}{1}".format(url,link['href'])
        self.root_folders = []
        self.files = {}
        self.folders = {}
        self.forms = {}

        self.session = None

    def get_param(self,link,param):
            found = re.search("{0}=(\d+)".format(param), link['href']).group(1)
            return found    

    def set_session(session):
        self.session = session

    def get_file_tree(self,session):
        self.session = session

        resp = self.session.get(self.url)
        soup = bs(resp.content, 'html.parser')
        folders = self.search_folder_and_files(soup,None)
        self.root_folders.append(folders)
        for folder in folders:
            self.get_folder(folder)
        
    def search_folder_and_files(self,soup,parent):
        folders = soup.find_all(
            'a', href=re.compile('acc_carp=abrir_carpeta'))
        files = soup.find_all(
            'a', href=re.compile('id_archivo'))
        
        _folders = []
        for folder in folders: 
            _id = self.get_param(folder,'id_carpeta')
            if _id in self.folders:
                continue
            _name = folder.text
            _url = "{0}{1}".format(urls['base'],folder['href'])
            _folder = Folder(_id,_name,_url,parent)
            _folders.append(_folder)
            self.folders[_id] = _folder
        for file_ in files:
            _id = self.get_param(file_,'id_archivo')
            if _id in self.files: 
                continue
            _name = file_.text
            _url = "{0}{1}".format(urls['base'],file_['href'])
            _file = File(_id,_name,_url,parent)
            self.files[_id] = _file

        return _folders

    def get_forms(self):
        resp = self.session.get(urls['forms'].format(self.course_id))
        soup = bs(resp.content, 'html.parser')
        tables_forms = soup.find_all('table', class_='ColorFondoSubHeader2')
        for table in tables_forms:
            form_name = table.td.text.strip()
            form_id = self.get_param(table.a,'id_cuest')
            self.forms[form_name] = form_id

        return self.forms

    def get_folder(self,folder):
        resp = self.session.get(folder.url)
        soup = bs(resp.content, 'html.parser')
        folders = self.search_folder_and_files(soup,folder)

    def __str__(self):
        return "{0} {1} {2}".format(self.course_id,self.acronym,self.name)
    def __repr__(self):
        return "{0} {1} {2}".format(self.course_id,self.acronym,self.name)