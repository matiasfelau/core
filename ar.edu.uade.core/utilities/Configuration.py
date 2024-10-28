import configparser

from utilities.Files import check_path, check_create_path
from utilities.Utilities import check_void_parameter

PATH = '/core_data/resources/config.ini'


def initialize_configuration_reader(path='/core_data/resources/config.ini'):
    """
    Inicializa el lector del archivo de configuración.
    :return: Devuelve el lector para su uso.
    """
    try:
        path = check_void_parameter(path, PATH)
        reader = configparser.ConfigParser()
        check_create_configuration_file(reader, path)
        reader.read(path)
        return reader
    except Exception as e:
        print(f'\nError in utilities.configuration.initialize_configuration_reader(): \n{str(e)}')
        return None


def check_create_configuration_file(reader, path):
    """

    :return:
    """
    try:
        #Obtiene la ruta del directorio al que pertenece el archivo.
        file_directory_path = path.rpartition('/')[0]

        if check_path(path):
            check_create_path(file_directory_path)
            create_configuration_file(reader)
    except Exception as e:
        print(f'\nError in utilities.configuration.initialize_configuration_reader(): \n{str(e)}')
        raise Exception


def read_configuration_attribute(reader, sector, attribute):
    """
    Recupera el valor asignado a una key contenida dentro de un grupo de variables del archivo de configuración.
    :param sector: Requiere el nombre del sector al que pertenece la variable.
    :param attribute: Requiere la key por la que se obtendría el valor.
    :param reader: Requiere al lector del archivo que se consigue con initialize_configuration_reader()
    :return: Devuelve el valor o None si ocurrió una excepción.
    """
    try:
        return reader[sector][attribute]
    except Exception as e:
        print(f'\nError in utilities.configuration.read_configuration_attribute(): \n{str(e)}')
        return None


def create_configuration_file(reader, path='/core_data/resources/config.ini'):
    """
    Crea el archivo de config.ini.
    :param path:
    :param reader: Requiere al lector del archivo que se consigue con initialize_configuration_reader()
    :return:
    """
    try:
        path = check_void_parameter(path, PATH)
        with open(path, 'w') as configfile:
            reader.write(configfile)
    except Exception as e:
        print(f'\nError in utilities.configuration.create_configuration_file(): \n{str(e)}')
        raise Exception


def write_in_configuration_file(module, attribute):
    """

    :param module:
    :param attribute:
    :return:
    """
