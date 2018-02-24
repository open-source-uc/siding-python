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
        self.conn = aiohttp.TCPConnector(limit=2)
        self.session = self.loop.run_until_complete(
            self._create_session(connector=self.conn))
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.logged = False

    async def _create_session(self, *args, **kwargs):
        session = aiohttp.ClientSession(*args, **kwargs)
        return session

    def login(self, user=None, password=None):
        return self.loop.run_until_complete(self._login(user, password))

    async def _login(self, user=None, password=None):

        payload = {
            'login': os.environ['USER'] if not(user) else user,
            'passwd': os.environ['PASSWD'] if not(password) else password,
            'sw': '',
            'sh': '',
            'cd': ''
        }
        async with self.session.post(urls['login'], data=payload) as resp:
            data = await resp.text()
            self.logged = self._check_successful_login(data)
            if self.logged:
                self.logger.info('Successful', extra={'method': 'LOGIN'})
                return "Login Successful"
            self.logger.error("Access Denied", extra={'method': 'LOGIN'})
            return "Access Denied"

    def new_folder(self, course_id, folder_name, parent_id=None, privacidad='publico'):
        data = {
            'orden_orig': '',
            'orden': "4",  #Al final
            'nombre_carpeta': folder_name,
            'privacidad': privacidad
        }
        if parent_id:
            data['id_parent'] = parent_id
            resp = self._session.post(
                urls['new_subfolder'].format(course_id),
                data=data,
            )
        else: 
            resp = self._session.post(
                urls['new_folder'].format(course_id),
                data=data,
            )
        return resp

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

    def _check_successful_login(self, resp):
        soup = bs(resp, 'html.parser')
        login_fail = soup.find_all(
            'b', string=re.compile("Datos de ingreso incorrectos"))
        if len(login_fail) >= 1:
            return False
        return True

    def __del__(self):
        print("Destruyendo la instancia")
        self.destroy()

    def destroy(self):
        self.session.close()

