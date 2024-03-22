<?php
defined('MOODLE_INTERNAL') || die();

$functions = array(
    'local_actualizarportada_actualizar_imagen_portada' => array(
        'classname'   => 'local_actualizarportada_external',
        'methodname'  => 'actualizar_imagen_portada',
        'classpath'   => 'local/actualizarportada/externallib.php',
        'description' => 'Actualizar la imagen de portada de un curso',
        'type'        => 'write',
        'ajax'        => true,
        'services' => array(MOODLE_OFFICIAL_MOBILE_SERVICE)
    ),
);