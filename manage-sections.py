import requests


from log import cool_print

# Logear al siding 
# Crear Tarea 
def logger(f):
	def inner(*args, **kwargs):
		cool_print("Calling Siding function {}".format(f.__name__))
		cool_print("\tArguments: %s, %s" % (args, kwargs))
		return f(*args, **kwargs)
	return inner

urls = {
	'nuevo-aviso': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml'
				   '?accion_curso=avisos&acc_aviso=nuevo&id_curso_ic={}',
	'lista-curso': 'https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/cursos/index.phtml?'
				   'accion_curso=alumnos&acc_alumnos=mostrar_lista&id_curso_ic={}',
}



@logger
def post_notice(subject, file_name):
	text = storage.load_text_file(file_name)
	if len(text) == 0:
		return

	for section in config.sections.values():
		self.driver.get(url['nuevo-aviso'].format(section['siding-id']))
		content_field = self.driver.find_element_by_name("contenido_aviso")
		subject_field = self.driver.find_element_by_name("asunto")
		content_field.send_keys(text)
		subject_field.clear()
		subject_field.send_keys(subject)
		subject_field.submit()


def upload_homework(folder,file)
	url = get_folder_url(folder)
	pass