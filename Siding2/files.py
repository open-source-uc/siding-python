from . import Siding
from .urls import urls

from bs4 import BeautifulSoup as bs
import asyncio
import re
import json
import itertools


class Files():

  @staticmethod
  def download(fpath, url):
    Siding.loop.run_until_complete(Files._download(fpath, url))

  @staticmethod
  async def _download(fpath, url):
      async with Siding.session.get(url) as resp:
        Siding.logger.info('Downloading {0} [{1}]'.format(
          fpath, resp.status), extra={'method': 'DOWNLOAD'})
        with open(fpath, 'wb') as f:
          while True:
            chunk = await resp.content.read(1024)
            if not chunk:
                break
            f.write(chunk)
  
  @staticmethod
  def bulk_download():
    questionnaire = Siding.questionnaire(
      "https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?accion_curso=cuestionarios&acc_cuest=ver_respuestas&ver_por=matriz&id_cuest=15168&id_curso_ic=9151")
    files = itertools.chain(
      *map(lambda answer: answer['answers'], questionnaire))
    all_tasks = [Files._download(
      'testing/' + file['name'], file['url']) for file in files]
    all_tasks = Siding.loop.run_until_complete(
      asyncio.gather(*(all_tasks[:])))