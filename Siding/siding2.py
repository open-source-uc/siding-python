import os
import re

from requests import Request, Session

from bs4 import BeautifulSoup as bs
from course import Course
from organization import Organization
from decorators import check
import time 

#from . import types as SidingTypes

class Siding():
    _instance = None
    

    _urls = {
        'login': 'https://intrawww.ing.puc.cl/siding/index.phtml',
        'base': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/',
        'aviso': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=avisos&acc_aviso=ingresar_aviso&id_curso_ic={0}',
        'folder': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=insert_carpeta&id_curso_ic={0}&volver_carpetas',
        'subfolder': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=insert_subcarpeta&id_curso_ic={0}&volver_carpetas',
        'new_file': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=insert_archivo&id_curso_ic={0}&id_carpeta={1}',
        'del_file': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=borrar_archivo&id_curso_ic={0}&id_carpeta={1}&id_archivo={2}',
        'courses': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml',
        'new_form': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=insert_cuest&id_curso_ic={0}',
        'del_form': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=borrar_cuest&id_cuest={1}&id_curso_ic={0}',
        'add_question': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=nueva_pregunta&id_cuest={1}&id_curso_ic={0}'
    }

    def __new__(class_, *args, **kwargs):
      if not isinstance(class_._instance, class_):
        class_._instance = object.__new__(class_, *args, **kwargs)
      return class_._instance

    def __init__(self):
        self.organizations = {}
        self.login()

    def login(self,user = None, password = None): # Cambiar
        if hasattr(self,'logged') and self.logged:
          return None
        _urls = Siding._urls
        payload = {
            'login': os.environ['USER'] if not(user) else user,
            'passwd': os.environ['PASSWD'] if not(password) else password,
            'sw': '',
            'sh': '',
            'cd': ''
        }
        self._session = Session()
        resp = self._session.post(_urls['login'], data=payload)
        if resp.status_code == 200:
          self.logged = self.__check_successful_login(resp)
        return resp
    
    def __check_successful_login(self,resp):
        soup = bs(resp.content, 'html.parser')
        login_fail = soup.find_all('b', string=re.compile("Datos de ingreso incorrectos"))
        if len(login_fail) >= 1:
            return False
        return True

    def post_notice(self, nrc, curso, asunto, aviso):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=iso-8859-1"}
        _urls = Siding._urls
        _asunto = '{0} - {1}'.format(curso, asunto)

        payload = {
            'asunto': _asunto,
            'contenido_aviso': aviso.encode('iso-8859-1')
        }
        headers = {

        }
        resp = self._session.post(
            _urls['aviso'].format(nrc),
            data=payload,
            headers=headers
        )

        return resp
    def new_folder(self, course_id, folder_name, parent_id=None, privacidad='publico'):
        data = {
            'orden_orig': '',
            'orden': "4",  #Al final
            'nombre_carpeta': folder_name,
            'privacidad': privacidad
        }
        if parent_folder:
            data['id_parent'] = parent_id
            resp = self._session.post(
                _urls['subfolder'].format(course_id),
                data=data,
            )
        else: 
            resp = self._session.post(
                _urls['folder'].format(course_id),
                data=data,
            )
        return resp,
    def upload_file(self, course_id, folder_id, desc, ffile, filepath=None, pos=2, vis='si'):
        if not(vis in ['si', 'no']):
            vis = 'no'
        if not(filepath):
            filepath = ffile

        _urls = Siding._urls
        data = {
            'orden_orig': None,
            'descripcion_archivo': desc,
            'orden': str(pos),
            'es_visible': vis,
            'MAX_FILE_SIZE': '104857600'
        }
        files = {
            'archivo_up': (ffile, open(filepath, 'rb'))
        }

        resp = self._session.post(
            _urls['new_file'].format(course_id, folder_id),
            data=data,
            files=files
        )
        return resp

    def delete_file(self, course_id, folder_id, file_id):
        _urls = Siding._urls
        resp = self._session.get(
            _urls['del_file'].format(course_id, folder_id, file_id))
        return resp

    #@format(*SidingTypes.NEW_FORM_FORMATS)
    #@check(*SidingTypes.NEW_FORM_TYPES)
    def new_form(self, course_id, name, start_date, start_time, end_date, end_time, resend='SI'):        
        _urls = Siding._urls
        
        start_time = start_time.split(":")
        end_time = end_time.split(":")
        
        data = {
            'nombre_cuestionario': name,
            'fecha_inicio': start_date,  # dia-mes-año
            'hora_inicio_HH': str(int(start_time[0])),
            'hora_inicio_mm': str(int(start_time[1])),
            'fecha_fin': end_date,
            'hora_fin_HH': str(int(end_time[0])),
            'hora_fin_mm': str(int(end_time[1])),
            'respuesta_modificable': resend  # SI o NO
        }
        resp = self._session.post(
            _urls['new_form'].format(course_id),
            data=data,
        )
        result = re.search(r'\?accion_curso=cuestionarios&acc_cuest=nueva_pregunta&id_cuest=(\d+)',resp.text)
        return resp,result.group(1)
    def delete_form(self,course_id,form_id):
        _urls = Siding._urls
        resp = self._session.get(
            _urls['del_form'].format(course_id, form_id))
        return resp
    def form_add_question(self,course_id,form_id,question):
        _urls = Siding._urls

        data = {
            'enunciado_pregunta': None,
            'descripcion_archivo': None,
            'radTipoRespuesta': None, # TextoCorto, Archivo, TextoLargo,SelMultiple_1resp
            'MAX_FILE_SIZE': '104857600',
            'txtAlternativaA':'',
            'txtAlternativaB':'',
            'txtAlternativaC':'',
            'txtAlternativaD':'',
            'txtAlternativaE':'',
            'txtAlternativaF':''
        }
        files = {
            'archivo_apoyo': (ffile, open(ffile, 'rb'))
        }

        resp = self._session.post(
            _urls['add_question'].format(course_id,form_id),
            data=data,
        )
        
    def _get_courses(self, soup, string):
        td = soup.find_all('td', string=re.compile(string))
        links = self.get_links_from_table(td[0])
        return links

    def get_courses(self):
        _urls = Siding._urls
        resp = self._session.get(_urls['courses'])
        soup = bs(resp.content, 'html.parser')

        courses = self._get_courses(soup, 'alumno')
        admin = self._get_courses(soup, "administrador")
        teaching = self._get_courses(soup, "donde es ayudante")

        #self.courses = [Course(_urls['base'],curso) for curso in courses]
        self.admin = [Course(_urls['base'],curso) for curso in  admin]
        #self.teaching = [Course(_urls['base'],curso) for curso in teaching]

        #[(course.get_file_tree(self._session)) for course in self.courses]
        [(course.get_file_tree(self._session)) for course in self.admin]
        #[(course.get_file_tree(self._session)) for course in self.teaching]
        
        self.organizations = self.create_organizations(self.admin)

        #this should return a json response 
        return 'chao'

    def create_organizations(self,courses):
        organizations = {}
        for course in courses:
            if not(course.acronym in organizations):
                organizations[course.acronym] = []
            organizations[course.acronym].append(course)
        organizations = {acronym:Organization(courses,self) 
            for acronym,courses in organizations.items()}
        return organizations

    def get_links_from_table(self, td):
        table = td.parent.parent
        links = table.find_all('a', href=re.compile(
            '\?accion_curso=avisos&acc_aviso=mostrar&id_curso_ic='))
        return links

def main():
    s1 = Siding()
    s1.get_courses()
    iic = s1.organizations['IIC1103']
    #iic.delete_file('rubrica_t3.xlsx')
    iic.upload_file('Interrogaciones','Interrogacion 2','interrogacion2.pdf','/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Is/Interrogacion 2/iic1103-enunciado-i2.pdf')
    #iic.upload_file('Interrogaciones Pasadas','Compilados I2s','compilado_i2.zip','/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Material/Interrogaciones Pasadas/Interrogacion 2/PreparacionI2.zip')
    #print(iic.new_form('Tarea 2','03-05-2017','00:00','17-05-2017','23:59'))
    # print(iic.new_form())
    #	r = s.upload_homework(desc,ffile)
    # print(r.text)
    # print(r.status_code)

    #r2 = s.delete_file()
    # print(r2.text)
    # print(r2.status_code)

    #s.new_form('1','2','3','4','5','6','SI')
if __name__ == '__main__':
    main()

