<?php
defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . "/externallib.php");

class local_actualizarportada_external extends external_api {

    public static function actualizar_imagen_portada_parameters() {
        return new external_function_parameters(
            array(
                'courseid' => new external_value(PARAM_INT, 'ID del curso'),
                'filename' => new external_value(PARAM_TEXT, 'Nombre del archivo'),
                'imagen' => new external_value(PARAM_RAW, 'Imagen en base64')
            )
        );
    }

    public static function actualizar_imagen_portada($courseid, $filename, $imagen) {
        global $CFG, $DB, $USER;

        // Verificar y validar los parámetros.
        $params = self::validate_parameters(
            self::actualizar_imagen_portada_parameters(),
            array(
                'courseid' => $courseid,           
                'filename' => $filename,
                'imagen' => $imagen
            )
        );

        // Verificar si el curso existe.
        $course = $DB->get_record('course', array('id' => $params['courseid']), '*', MUST_EXIST);

        // Verificar los permisos del usuario.
        $context = context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:update', $context);

        // Decodificar la imagen en base64.
        $decoded_image = base64_decode($params['imagen']);

        // Crear un objeto stdClass para almacenar los detalles del archivo.
        $file_record = new stdClass();
        $file_record->component = 'course';
        $file_record->filearea = 'overviewfiles';
        $file_record->itemid = 0;
        $file_record->contextid = $context->id;
        $file_record->filepath = '/';
        $file_record->filename = $params['filename']; // O el nombre de archivo que prefieras.

        // Obtener la instancia de file_storage.
        $fs = get_file_storage();
	
	
    	// Eliminar todas las imágenes de portada existentes.
    	$files = $fs->get_area_files($context->id, 'course', 'overviewfiles', 0, "filename", false);
    		foreach ($files as $file) {
        	$file->delete();
    	}

        // Verificar si ya existe un archivo con el mismo nombre en la carpeta 'overviewfiles'.
        if ($existing_file = $fs->get_file($file_record->contextid, $file_record->component, $file_record->filearea, $file_record->itemid, $file_record->filepath, $file_record->filename)) {
            // Eliminar el archivo existente.
            $existing_file->delete();
        }

        // Crear el archivo en Moodle utilizando la API de funciones de archivos.
        $fs->create_file_from_string($file_record, $decoded_image);

	
    	// Borrar el caché de Moodle.
    	if ($CFG->version >= 2018051700) { // Moodle 3.5 o superior
        	cache_helper::purge_by_event('changesincourse');
    	} else {
        	cache_helper::purge_by_event('changesincourse', $course);
    	}


    	// Purge all caches
        purge_all_caches(); 

        return array('status' => 'success');
    }


   public static function actualizar_imagen_portada_returns() {
    	return new external_single_structure(
            array(
                'status' => new external_value(PARAM_TEXT, 'Estado de la operación')
            )
        );
    }

}