from . import Siding
from .urls import urls

from bs4 import BeautifulSoup as bs
import asyncio
import re
import json

class Courses():
    def __init__(self):
        self.loop = Siding.loop
        self.session = Siding.session
        self.logger = Siding.logger
        self.courses = {}
    
    def get_param(self, link, param):
            found = re.search("{0}=(\d+)".format(param), link['href']).group(1)
            return found

    def get_links_from_table(self, td):
            table = td.parent.parent
            links = table.find_all('a', href=re.compile(
                '\?accion_curso=avisos&acc_aviso=mostrar&id_curso_ic='))
            return links

    async def _get_courses_links(self, soup, string):
            td = soup.find_all('td', string=re.compile(string))
            if td:
                links = self.get_links_from_table(td[0])
                return links
            return []

    def get_courses(self):
        tasks = self.loop.run_until_complete(self._get_courses())
        all_tasks = [item for sublist in tasks.values() for item in sublist]
        results = self.loop.run_until_complete(asyncio.gather(*all_tasks))
        '''  for course in all_tasks:
            print(course['course'])
            with open('{}.json'.format(course['course']), 'w') as file:
                json.dump(course,file,indent=4) '''
        return all_tasks

    async def _get_courses(self):
        # hacer gather de tasks para los await aqui
        async with self.session.get(urls['courses']) as resp:
            data = await resp.text()
            soup = bs(data, 'html.parser')
            # buscar un soup más pequeño para optimizar aqui
            courses = await self._get_courses_links(soup, 'alumno')
            admin = await self._get_courses_links(soup, 'administrador')
            teaching = await self._get_courses_links(soup, 'donde es ayudante')

            courses = [self._get_course(course) for course in courses]
            admin = [self._get_course(course) for course in admin]
            teaching = [self._get_course(course) for course in teaching]
            tasks = {'courses': courses, 'admin': admin, 'teaching': teaching}
            return tasks

    async def _get_course(self,course):
        link = "{0}{1}".format(urls['base'], course['href'])
        course = {
                'acronym': course.text.split()[0],
                'course_id': self.get_param(course, 'id_curso_ic'),
                'url': link,
                'course': course.text,
                'section': '',
                'folders': {},
                'files': {}
        }
        self.logger.info("%s" %course['course'] ,extra={"method": 'GET COURSE'})
        self.courses[course['course_id']] = course
        return course

    async def _get_course_info(self, course):
        link = "{0}{1}".format(urls['base'], course['href'])
        course =  await self._get_course_file_tree(link, course)
        self.logger.info("%s" %course['course'] ,extra={"method": 'GET COURSE INFO'})
        return course

    async def _get_course_file_tree(self, link, course):
        folders = {}
        files = {}
        _course = course
        course = {
            'acronym': course.text.split()[0],
            'course_id': self.get_param(course, 'id_curso_ic'),
            'url': link,
            'course': course.text,
            'section': '',
            'folders': folders,
            'files': files
        }
        async with self.session.get(link) as resp:
            if resp.status == 500:
                self.logger.warning("[ RETRY ]{0}".format(link), extra={'method': 'FILE TREE'})
                await asyncio.sleep(1)
                await self._get_course_file_tree(link, _course)
            else:
                self.logger.warning("[ SUCCESS ]{0}".format(link), extra={'method': 'FILE TREE'})
                data = await resp.text()
                soup = bs(data, 'html.parser')
                _folders = await self._search_folder_and_files(soup, None, folders, files)
                for folder in _folders:
                    await self.get_course_folder(folder, folders, files)
        return course

    async def get_course_folder(self, folder, folders, files):
        async with self.session.get(folder['url']) as resp:
            if resp.status == 500:
                self.logger.warning("[ RETRY ]{0}".format(folder['name']), extra={'method': 'FOLDER'})
                await asyncio.sleep(1)
                await self.get_course_folder(folder, folders, files)
            else:
                self.logger.warning("[ SUCCESS ]{0}".format(folder['name']), extra={'method': 'FOLDER'})
                data = await resp.text()
                soup = bs(data, 'html.parser')
                folders_ = await self._search_folder_and_files(soup, folder['id'], folders, files)
                folder['folders'] = list(map(lambda f: f['id'], folders_))
                for folder in folders_:
                    await self.get_course_folder(folder, folders, files)
            

    async def _search_folder_and_files(self, soup, parent, folders, files):
        ''' if parent:
            print("[ FOLDER ]{0}".format(folders[parent]['name'])) '''
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