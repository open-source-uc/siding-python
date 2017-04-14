from siding import Siding

sigla = "IIC1103"
cursos = ['9151','9334','9239','9422','9441','9289']
aviso = '''Estimados,

Se encuentra abierto el cuestionario para subir la Tarea 1. En este pueden enviar múltiples veces las respuestas de su tarea y la última respuesta borrará la anterior, para que vayan subiendo avances y no dejen esto para último momento.
Además se encuentra publicada una rúbrica para la Tarea 1, en la carpeta Tareas/Tarea 1

Saludos,
Equipo de Coordinación.''' 

def avisos():
  s = Siding()
  for curso in cursos[:4]:
    s.post_notice(curso,sigla,'Relacionados Tarea 1',aviso)

def abrir_formulario():
  s = Siding()
  for curso in [cursos[0]]:
    resp,cuestionario = s.new_form(curso,'Testing','12-04-2017','00:00','17-04-2017','23:59')
    print(resp.text)
    print(cuestionario)

def main():
  abrir_formulario()
if __name__ == '__main__':
  main()

