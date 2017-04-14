import os
import re

from requests import Request, Session

from bs4 import BeautifulSoup as bs
from course import Course
from decorators import check

import siding_types as SidingTypes

class Siding():
    _urls = {
        'login': 'https://intrawww.ing.puc.cl/siding/index.phtml',
        'base': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/',
        'aviso': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=avisos&acc_aviso=ingresar_aviso&id_curso_ic={0}',
        'new_file': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=insert_archivo&id_curso_ic={0}&id_carpeta={1}',
        'del_file': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=borrar_archivo&id_curso_ic={0}&id_carpeta={1}&id_archivo={2}',
        'courses': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml',
        'new_form': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=insert_cuest&id_curso_ic={0}',
        'add_question': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=nueva_pregunta&id_cuest={1}&id_curso_ic={0}'
    }

    def __init__(self):
        self.login()

    def login(self):

        _urls = Siding._urls
        payload = {
            'login': os.environ['USER'],
            'passwd': os.environ['PASSWD'],
            'sw': '',
            'sh': '',
            'cd': ''
        }
        self._session = Session()
        resp = self._session.post(_urls['login'], data=payload)
        return resp

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

    def upload_homework(self, course_id, folder_id, desc, ffile, filepath=None, pos=2, vis='si'):
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
            'archivo_up': (ffile, open(ffile, 'rb'))
        }

        resp = self._session.post(
            _urls['new_file'].format(nrc, folder),
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
        return resp,result.group(0)

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
        

        pass
    def _get_courses(self, soup, string):
        td = soup.find_all('td', string=re.compile(string))
        links = self.get_links_from_table(td[0])
        return links

    def get_courses(self):
        _urls = Siding._urls
        resp = self._session.get(_urls['courses'])
        soup = bs(resp.content, 'html.parser')

        cursos = self._get_courses(soup, 'alumno')
        administracion = self._get_courses(soup, "administrador")
        ayudantias = self._get_courses(soup, "donde es ayudante")
        #[self.get_course_treefor course in cursos]
        self.get_course_tree(cursos[1]['href'])

    def get_course_tree(self, url):
        base = Siding._urls['base']
        _url = base + url
        print(_url)

        resp = self._session.get(_url)
        soup = bs(resp.content, 'html.parser')
        carpetas = soup.find_all(
            'a', href=re.compile('acc_carp=abrir_carpeta'))
        print(carpetas)

    def get_links_from_table(self, td):
        table = td.parent.parent
        links = table.find_all('a', href=re.compile(
            '\?accion_curso=avisos&acc_aviso=mostrar&id_curso_ic='))
        return links

def main():
    s = Siding()
    #print(s._session.cookies)
    # print(s.get_page('https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=carpetas&acc_carp=borrar_archivo&id_curso_ic=9151&id_carpeta=56865&id_archivo=357336').text)
    desc = "Test"
    ffile = "log.py"
#	r = s.upload_homework(desc,ffile)
    # print(r.text)
    # print(r.status_code)
    #s.get_courses()

    #r2 = s.delete_file()
    # print(r2.text)
    # print(r2.status_code)

    s.new_form('1','2','3','4','5','6','SI')
if __name__ == '__main__':
    main()

