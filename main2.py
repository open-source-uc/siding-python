from Siding2 import Siding
from Siding2.course import Courses
from Siding2.files import Files
import asyncio

def main():
  Siding.login('mjjunemann','nxfku595')
  #Files.bulk_download()
  c = Courses()
  c.get_courses()

if __name__ == '__main__':
  main()