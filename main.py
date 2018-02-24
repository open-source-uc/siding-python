from siding import Siding
import time
sigla = "IIC1103"
cursos = ['9881','9867','9882','9802','9865','9869','9854','9883','9732']
#cursos = ['9151','9334','9422','9441','9289']
#cursos = ['9151','9422','9441']
#cursos = ['9239']
tareas = []
ies_pasadas = ['57298','57299','57300','57301','57302','57303']
archivos = ["/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Material/Interrogaciones Pasadas/Compilado_i1_2013-2_2016-2.zip",
            "/Users/mjjunemann/GDrive/Universidad - Ayudantias/Intro2017_1/Is/Interrogacion 1/recordatorio-i1-2017-1.pdf"]
file_names = ['compilado_i1.zip','recordatorio_i1.pdf']

descs = ['Compilado de Interrogaciones 1', 'Recordatorio de contenidos I1']

aviso = '''Estimados estudiantes,

Como ya saben, esta semana tenemos un laboratorios distinto,
ya que la plataforma Hackerrank no permite trabajar con archivos.
Lo más importante: les recomendamos fuertemente asistir a los laboratorios
esta semana para poder aclarar sus dudas sobre el laboratorio o sobre el tester.

Algunos problemas comunes que hemos encontrado son:
* Uso de input(): Al igual que en Hackerrank, deben utilizar la función input sin parámetros.
* Python no es un comando válido. Si te aparece un error similar es porque python
no ha sido agregado al PATH. Para solucionarlo fácilmente puedes volver a entrar al
instalador de python (o volver a decargarlo) y marcar la opción "Add Python 3.6 to PATH"
o "Agregar python a las variables de entorno".
* Timeout en todos los casos: Es posible que en windows tu programa toma más tiempo
que el esperado, para esto puedes modificar el archivo tester.py. En las líneas que dice
result = subprocess.call(cmd, shell=True, stdout=outfile, stderr=outfile, timeout=1),
debes modificar la variable timeout y aumentar su valor (por ejemplo, timeout=5).

Además, el día domingo en la noche se subió una versión actualizada del tester.

Saludos,
Equipo de coordinación.
''' 

def avisos(aviso,asunto):
  s = Siding()
  for curso in cursos:
    time.sleep(2)
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
  s = Siding()
  #print(s.get_courses())
  #abrir_formulario()
  #subir_archivos(ies_pasadas,archivos,file_names,descs)
  avisos(aviso,'Laboratorio')

if __name__ == '__main__':
  main()

