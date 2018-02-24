from siding import Siding
import time
sigla = "SIGLA DEL CURSO"
cursos = ['AGREGAR CURSOS']

titulo = 'Tarea 1'
aviso = '''Estimados,

Se ha publicado el enunciado de la Tarea 1, y lo pueden encontrar en la carpeta Tareas del Siding. Tienen hasta el viernes 15 de septiembre a las 23:50 horas para subir su solución al Siding. Cualquier duda de encunciado, pueden preguntar en el [piazza.com/uc.cl/summer2017/iic1103/home foro] del curso. Este es el medio oficial para sus preguntas. Por esto, quienes aún no se han inscrito, deben hacerlo a la brevedad.

Saludos,
Equipo de coordinación.
''' 

def avisos(s, aviso,asunto):
  for curso in cursos:
    time.sleep(2)
    s.post_notice(curso,sigla,asunto,aviso)

def main():
  s = Siding()
  s.login('USUARIO','PASSWORD')
  avisos(s, aviso,titulo)
if __name__ == '__main__':
  main()

