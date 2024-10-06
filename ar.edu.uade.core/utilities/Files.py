import os


def check_path(path):
    """
    Valida que exista la ruta especificada.
    :param path: Requiere la ruta.
    :return: Devuelve un boolean o None si ocurrió una excepción.
    """
    try:
        return os.path.exists(path)
    except Exception as e:
        print(f'\nError in utilities.files.check_path(): \n{str(e)}')
        return None


def check_create_path(path):
    """
    Valida que exista la ruta especificada y si no existe la crea.
    :param path: Requiere la ruta.
    :return:
    """
    try:
        #Obtiene los directorios de la ruta.
        directories = path.split('/')

        directories_quantity = len(directories)

        #Reconstruye parcialmente la ruta final con cada directorio.
        partial_path = f'/{directories[0]}'

        for i in range(directories_quantity):
            if not check_path(partial_path):
                #Crea el directorio.
                os.makedirs(partial_path)

            if (i + 1) < directories_quantity:
                #Reconstruye parcialmente la ruta final con cada directorio.
                partial_path += f'/{directories[i + 1]}'
    except Exception as e:
        print(f'\nError in utilities.files.check_create_path(): \n{str(e)}')
        raise Exception
