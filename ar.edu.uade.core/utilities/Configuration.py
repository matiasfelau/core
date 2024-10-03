import configparser
import os

from utilities.Logs.Messaging import check_path


def initialize_configuration_reader():
    """
    Inicializa el lector del archivo de configuración.
    :return: Devuelve el lector para su uso.
    """
    reader = configparser.ConfigParser()
    #path = './ar.edu.uade.core/resources/config.ini'
    path = '/core_disk/resources/config.ini'
    if not os.path.exists(path):
        write_default_configuration_file(reader)
    else:
        reader.read(path)
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


def write_default_configuration_file(reader):
    """

    :return:
    """
    reader['e_commerce'] = {
        'max_retries': '3',
        'min_ttl': '30000'
    }
    reader['gestion_financiera'] = {
        'max_retries': '3',
        'min_ttl': '30000'
    }
    reader['gestion_interna'] = {
        'max_retries': '3',
        'min_ttl': '30000'
    }
    reader['usuario'] = {
        'max_retries': '3',
        'min_ttl': '30000'
    }

    path = '/core_disk/resources/config.ini'

    with open(path, 'w') as configfile:
        reader.write(configfile)
