# Servicio Web de Actualización de Portada para Moodle

Este servicio web proporciona una interfaz para actualizar la imagen de portada de los cursos en Moodle de forma automatizada. Es compatible con Moodle versión 3 en adelante y se puede utilizar para mantener las portadas de los cursos actualizadas con imágenes relevantes desde otros sistemas o servicios.

## Características

- Compatibilidad con Moodle versión 3 en adelante.
- Actualización automática de la imagen de portada de cursos.
- Integración con sistemas externos a través de un script en Python.

## Cómo se ve el Servicio

![Vista del Servicio Web en Moodle](https://integrasoluc.net/media/moodle_.png)

## Ejemplo de Portada Actualizada

![Ejemplo de Portada Actualizada](https://integrasoluc.net/media/moodle_1.png)


## Instalación

Para instalar el servicio web de actualización de portada en tu instalación de Moodle:

1. Asegúrate de que estás ejecutando Moodle versión 3 o superior.
2. Sube los contenidos de la carpeta `moodle_servicio` al directorio `/Moodle/local/` en tu servidor.
3. Inicia sesión en tu sitio Moodle como administrador. El servicio debería aparecer como `local_actualizarportada_actualizar_imagen_portada` en la sección de servicios web.
4. Sigue las instrucciones en pantalla para completar la instalación.

## Uso

Después de instalar el servicio, puedes actualizar las portadas de los cursos utilizando el script `actualizar_moodle.py` proporcionado. Asegúrate de reemplazar los valores de las variables con la información correspondiente a tu entorno.

### Ejemplo de Script en Python

```python
import time
from datetime import datetime
import requests
import base64
import os
from django.db import connections

# Configura tus parámetros aquí
course_id = 'ID_DEL_CURSO'
image_path = 'RUTA_A_LA_IMAGEN'
file_name = 'NOMBRE_DEL_ARCHIVO'
urlmoodle = 'URL_DE_TU_MOODLE'
keymoodle = 'TU_TOKEN_DE_SERVICIO_WEB'

try:
    # Preparar la imagen codificada en base64
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # URL completa del servicio web
    moodle_url = f"{urlmoodle}/webservice/rest/server.php"

    # Configurar los parámetros para la llamada al servicio web.
    params = {
        'wstoken': keymoodle,
        'moodlewsrestformat': 'json',
        'wsfunction': 'local_actualizarportada_actualizar_imagen_portada',
        'courseid': course_id,
        'filename': file_name,
        'image': base64_image
    }

    # Realizar la llamada al servicio web de Moodle.
    response = requests.post(moodle_url, data=params)
    if response.status_code == 200:
        print('La imagen de portada se actualizó correctamente.')
    else:
        print('Error al actualizar la imagen de portada:', response.text)

    # Conectar a Moodle para vaciar la caché del curso.
    conexion = connections['moodle_db']
    cursor = conexion.cursor()
    fecha = int(time.mktime(datetime.now().timetuple()))
    query = u"UPDATE mdl_course SET cacherev = %s WHERE id = %s" % (fecha, course_id)
    cursor.execute(query)

except Exception as ex:
    print('Ha ocurrido un error:', str(ex))

