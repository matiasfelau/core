import configparser
import os


def initialize_configuration_reader():
    """
    Inicializa el lector del archivo de configuración.
    :return: Devuelve el lector para su uso.
    """
    reader = configparser.ConfigParser()
    reader.read('./ar.edu.uade.core/resources/config.ini')
    return reader


def read_configuration_attribute(reader, group, attribute):
    """
    Recupera el valor asignado a una key contenida dentro de un grupo de variables del archivo de configuración.
    :param group: Requiere el nombre del grupo al que pertenece la variable.
    :param attribute: Requiere la key por la que se obtendría el valor.
    :param reader: Requiere al lector del archivo que se consigue con initialize_configuration_reader()
    :return:
    """
    return reader[group][attribute]

