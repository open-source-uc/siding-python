from siding import Siding

sigla = "IIC1103"
cursos = ['9151','9334','9239','9422','9441','9289']
tareas = []
ies_pasadas = ['57298','57299','57300','57301','57302','57303']
archivos = ["/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Material/Interrogaciones Pasadas/Compilado_i1_2013-2_2016-2.zip",
            "/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Is/Interrogacion 1/recordatorio-i1-2017-1.pdf"]
file_names = ['compilado_i1.zip','recordatorio_i1.pdf']

descs = ['Compilado de Interrogaciones 1', 'Recordatorio de contenidos I1']

aviso = '''Estimados,

Se encuentra subida la tarea 2.

Saludos,
Equipo de Coordinación.''' 

def avisos(aviso,asunto):
  s = Siding()
  for curso in cursos:
    s.post_notice(curso,sigla,asunto,aviso)

def abrir_formulario():
  s = Siding()
  for curso in cursos:
    resp,cuestionario = s.new_form(curso,'Testing','12-04-2017','00:00','17-04-2017','23:59')
    print(resp.text)
    print(cuestionario)

def subir_archivos(folders,files,file_names,descs):
  s = Siding()
  for course,folder in zip(cursos,folders):
    for archivo,name,desc in zip(files,file_names,descs):
      resp = s.upload_file(course,folder,desc,name,archivo)
      print(resp)

def main():
  #abrir_formulario()
  #subir_archivos(ies_pasadas,archivos,file_names,descs)
  avisos(aviso,'Tarea 2')
if __name__ == '__main__':
  main()

