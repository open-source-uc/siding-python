import asyncio
import aiofiles
import aiohttp
import uvloop
import os
import re
import json
import itertools
import logging

from .urls import urls
from bs4 import BeautifulSoup as bs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)10s] [%(method)15s] [%(levelname)s] %(message)s')  # Add method


class Siding():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        _loop = uvloop.new_event_loop()
        asyncio.set_event_loop(_loop)
        self.loop = asyncio.get_event_loop()
        self.conn = aiohttp.TCPConnector(limit=15)
        self.session = self.loop.run_until_complete(
            self.create_session(connector=self.conn))
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.logged = False

    async def create_session(self, *args, **kwargs):
        session = aiohttp.ClientSession(*args, **kwargs)
        return session

    def login(self, user=None, password=None):
        return self.loop.run_until_complete(self.__login(user, password))

    async def __login(self, user=None, password=None):

        payload = {
            'login': os.environ['USER'] if not(user) else user,
            'passwd': os.environ['PASSWD'] if not(password) else password,
            'sw': '',
            'sh': '',
            'cd': ''
        }
        async with self.session.get(urls['login'], params=payload) as resp:
            data = await resp.text()
            self.logged = self.__check_successful_login(data)
            if self.logged:
                self.logger.info('Successful', extra={'method': 'LOGIN'})
                return "Login Successful"
            self.logger.error("Access Denied", extra={'method': 'LOGIN'})
            return "Access Denied"

    def __check_successful_login(self, resp):
        soup = bs(resp, 'html.parser')
        login_fail = soup.find_all(
            'b', string=re.compile("Datos de ingreso incorrectos"))
        if len(login_fail) >= 1:
            return False
        return True

    def post_notice(self, course_id, curso, asunto, aviso):
        return self.loop.run_until_complete(self.__post_notice(course_id, curso, asunto, aviso))

    async def __post_notice(self, course_id, curso, asunto, aviso):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=iso-8859-1"
        }
        _asunto = '{0} - {1}'.format(curso, asunto)

        payload = {
            'asunto': _asunto.encode('iso-8859-1'),
            'contenido_aviso': aviso.encode('iso-8859-1')
        }

        async with self.session.get(urls['aviso'].format(nrc), params=payload, headers=headers) as resp:
            data = await resp.text()
            return data

    def get_links_from_table(self, td):
        table = td.parent.parent
        links = table.find_all('a', href=re.compile(
            '\?accion_curso=avisos&acc_aviso=mostrar&id_curso_ic='))
        return links

    async def __get_courses_links(self, soup, string):
        td = soup.find_all('td', string=re.compile(string))
        links = self.get_links_from_table(td[0])
        return links

    def get_course(self, link, base=True):
        if base:
            link = "{0}{1}".format(urls['base'], link['href'])
        return self.loop.run_until_complete(self.__get_course(link))

    async def __get_course(self, course):
        link = "{0}{1}".format(urls['base'], course['href'])
        course =  await self.__get_course_file_tree(link, course)
        self.logger.info("%s" %course['course'] ,extra={"method": 'GET COURSE'})
        return course

    async def __get_course_file_tree(self, link, course):
        folders = {}
        files = {}
        course = {
            'acronym': course.text.split()[0],
            'course_id': self.get_param(course, 'id_curso_ic'),
            'course': course.text,
            'section': '',
            'folders': folders,
            'files': files
        }
        async with self.session.get(link) as resp:
            data = await resp.text()
            soup = bs(data, 'html.parser')
            _folders = await self._search_folder_and_files(soup, None, folders, files)
            for folder in _folders:
                await self.get_course_folder(folder, folders, files)
        return course

    async def get_course_folder(self, folder, folders, files):
        async with self.session.get(folder['url']) as resp:
            data = await resp.text()
            soup = bs(data, 'html.parser')
            folders_ = await self._search_folder_and_files(soup, folder['id'], folders, files)
            folder['folders'] = list(map(lambda f: f['id'], folders_))
            for folder in folders_:
                await self.get_course_folder(folder, folders, files)

    async def _search_folder_and_files(self, soup, parent, folders, files):
        _folders = soup.find_all(
            'a', href=re.compile('acc_carp=abrir_carpeta'))
        _files = soup.find_all(
            'a', href=re.compile('id_archivo'))
        new_folders = []
        for folder in _folders:
            _id = self.get_param(folder, 'id_carpeta')
            if _id in folders:
                continue
            url = "{0}{1}".format(urls['base'], folder['href'])
            name = folder.text
            _folder = {
                'id': _id,
                'name': name,
                'url': url,
                'parent': parent,
                'files': [],
                'folders': []
            }
            folders[_id] = _folder
            new_folders.append(_folder)
        for file_ in _files:
            _id = self.get_param(file_, 'id_archivo')
            if _id in files:
                continue
            name = file_.text
            url = "{0}{1}".format(urls['base'], file_['href'])
            _file = {
                'id': _id,
                'name': name,
                'url': url,
                'parent': parent
            }
            files[_id] = _file
            if parent in folders:
                folders[parent]['files'].append(_id)
        return new_folders

    def get_param(self, link, param):
        found = re.search("{0}=(\d+)".format(param), link['href']).group(1)
        return found

    def get_courses(self):
        tasks = self.loop.run_until_complete(self.__get_courses())
        all_tasks = [item for sublist in tasks.values() for item in sublist]

        all_tasks = self.loop.run_until_complete(asyncio.gather(*all_tasks))
        '''for course in all_tasks:
            print(course['course'])
            print(json.dumps(course['folders'], indent=4))'''
        return all_tasks

    async def __get_courses(self):
        # hacer gather de tasks para los await aqui
        async with self.session.get(urls['courses']) as resp:
            data = await resp.text()
            soup = bs(data, 'html.parser')
            # buscar un soup más pequeño para optimizar aqui
            courses = await self.__get_courses_links(soup, 'alumno')
            admin = await self.__get_courses_links(soup, 'administrador')
            teaching = await self.__get_courses_links(soup, 'donde es ayudante')

            courses = [self.__get_course(course) for course in courses]
            admin = [self.__get_course(course) for course in admin]
            teaching = [self.__get_course(course) for course in teaching]

            tasks = {'courses': courses, 'admin': admin, 'teaching': teaching}
            return tasks

    async def new_folder(self, course_id, folder_name, parent_id=None, privacidad='publico'):
        data = {
            'orden_orig': '',
            'orden': "4",
            'nombre_carpeta': folder_name,
            'privacidad': privacidad
        }
        if parent_folder:
            data['id_parent'] = parent_id
            async with self.session.post(urls['subfolder'].format(course_id), data=data) as resp:
                return await resp.text()
        else:
            async with self.session.post(urls['subfolder'].format(course_id), data=data) as resp:
                return await resp.text()

    def questionnaire(self, url):
        return self.loop.run_until_complete(self.questionnaire_responses(url))

    async def questionnaire_responses(self, questionnaire_url):
        async with self.session.get(questionnaire_url) as resp:
            self.logger.info('Questionnaire {0} [{1}]'.format(
                questionnaire_url, resp.status), extra={'method': 'QUESTIONNAIRE'})
            data = await resp.text()
            soup = bs(data, 'html.parser')
            responses = soup.find_all(
                'table', {'class': 'TablaConBordeFinoLightblue'})[0].find_all('tr')
            headers = [child.text.strip().lower().replace(" ", "_")
                       for child in responses[0].find_all('td')]
            headers = ['n_alumno', 'nombre',
                       'paterno', 'materno'] + headers[4:]
            answers = []
            for row in responses[1:]:
                answer = {
                    'answers': []
                }
                columns = row.find_all('td')
                for index, child in enumerate(columns):
                    if index <= 3:
                        "n_alumno"
                        answer[headers[index]] = child.text.strip()
                    else:
                        question = {}
                        question['question'] = headers[index]
                        link = child.find('a')
                        question['text'] = child.text.strip()
                        if link:
                            question['name'] = child.text.strip()
                            question['url'] = "https://intrawww.ing.puc.cl" + \
                                link['href']
                        answer['answers'].append(question)
                        answers.append(answer)
            return answers

    def bulk_download(self):
        questionnaire = self.questionnaire(
            "https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=ver_respuestas&ver_por=matriz&id_cuest=15168&id_curso_ic=9151")
        files = itertools.chain(
            *map(lambda answer: answer['answers'], questionnaire))
        all_tasks = [self._download(
            'testing/' + file['name'], file['url']) for file in files]
        all_tasks = self.loop.run_until_complete(
            asyncio.gather(*(all_tasks[:])))

    def download(self, fpath, url):
        self.loop.run_until_complete(self._download(fpath, url))

    async def _download(self, fpath, url):
        async with self.session.get(url) as resp:
            # print(resp)
            self.logger.info('Downloading {0} [{1}]'.format(
                fpath, resp.status), extra={'method': 'DOWNLOAD'})
            with open(fpath, 'wb') as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

    def destroy(self):
        self.session.close()


def main():
    s = Siding()
    print(s.login())
    courses = s.get_courses()
    s.destroy()


if __name__ == '__main__':
    main()
