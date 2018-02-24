from . import Siding
from .urls import urls

from bs4 import BeautifulSoup as bs
import asyncio
import re
import json

class OrganizationManager():
    def __init__(self):
        self.loop = Siding.loop
        self.session = Siding.session
        self.logger = Siding.logger

    def create_organizations(self,courses):
        organizations = {}
        for course in courses:
            if not(course.acronym in organizations):
                organizations[course.acronym] = []
            organizations[course.acronym].append(course)
        organizations = {acronym:Organization(courses,self) 
            for acronym,courses in organizations.items()}
        return organizations

class Organization():
  def __init__(self):
      self.loop = Siding.loop
      self.session = Siding.session
      self.logger = Siding.logger

  def sync_organization():
    pass

  def new_notice():
    pass

  def new_folder():
    pass

  def upload_file():
    pass

  def delete_file():
    pass
  
  def delete_folder():
    pass
  
  def new_questionnaire():
    pass
  
  def download_questionnaire():
    pass
  

