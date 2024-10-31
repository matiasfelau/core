import logging
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from utilities.Files import check_create_path
from utilities.Utilities import check_void_parameter

PATH = '/core_data/logs'


def initialize_logging_for_messaging_errors(path='/core_data/logs'):
    """
    Inicializa el sistema de logeo para los errores de mensajería, los cuales se almacenarán en archivos.
    :return: Devuelve un manejador que requiere la aplicación para poder realizar los logs o None si ocurrió una excepción.
    """
    try:
        path = check_void_parameter(path, PATH)
        check_create_path(path)

        local_time = datetime.now() - timedelta(hours=3)

        #Inicializa un handler que crea un nuevo archivo con el cambio de fecha
        handler = TimedRotatingFileHandler(path + f'/{local_time.date()}.log', when='midnight', interval=1)

        #Define el tipo de logs que manejará este handler
        handler.setLevel(logging.ERROR)

        #Define el formato en el que se harán los logs
        formatter = logging.Formatter('%(asctime)s;%(message)s')

        #Fija el formato al handler
        handler.setFormatter(formatter)

        return handler
    except Exception as e:
        print(f'\nError in utilities.logger.initialize_logging_for_messaging_errors(): \n{str(e)}')
        return None


def log_messaging_error(app, reason, origin, destination, case):
    """
    Realiza un log de un error de mensajería.
    :param app: Requiere una instancia de la aplicación para hacer logs.
    :param reason: Requiere la razón de descarte que se obtiene con get_death_reason().
    :param origin: Requiere el origen del que proviene el mensaje, obtenido de su cuerpo.
    :param destination: Requiere el destino al que se dirigía el mensaje, obtenido de su cuerpo.
    :param case: Requiere el caso de uso por el que existe el mensaje, obtenido de su cuerpo.
    :return:
    """
    try:
        #Integra todas las variables en el mensaje de log
        mensaje = f'{reason};{origin};{destination};{case}'

        #Realiza el log
        app.logger.warning(mensaje)

    except Exception as e:
        print(f'\nError in utilities.logger.log_messaging_error(): \n{str(e)}')


def filtrar_lineas(archivo, filtro, campo, offset, date):
    """
    Recupera todas las líneas de un archivo que coincidan con un filtro específico en un campo dado.

    :param date:
    :param offset:
    :param archivo: Ruta del archivo a abrir.
    :param filtro: Valor que se busca en el campo especificado.
    :param campo: Campo en el que se aplicará el filtro ('datetime', 'reason', 'origin', 'destination' o 'case').
    :return: Lista de líneas que cumplen con el filtro.
    """
    if filtro == '':
        filtro = '*'
    if campo == '':
        campo = 'datetime'
    if offset == '':
        offset = ''
    if date == '':
        local_time = datetime.now() - timedelta(hours=3)
        date = f'/{local_time.date()}.log'
        print(date)
    else:
        date = '/'+date+'.log'
    campos = ['datetime', 'reason', 'origin', 'destination', 'case']
    try:
        indice_campo = campos.index(campo)
    except ValueError:
        raise ValueError(f"Campo '{campo}' no válido. Debe ser uno de: {', '.join(campos)}")
    lineas_filtradas = []
    with open(archivo+date, 'r') as f:
        b = False
        while len(lineas_filtradas) < 10:
            linea = f.readline()
            if linea == '':
                break
            elif b or offset == '':
                process_line(filtro, indice_campo, linea, lineas_filtradas)
            elif offset != '' and not linea.startswith(offset):
                continue
            else:
                process_line(filtro, indice_campo, linea, lineas_filtradas)
                b = True
    return lineas_filtradas


def process_line(filtro, indice_campo, linea, lineas_filtradas):
    partes = linea.strip().split(';')
    if len(partes) == 5:
        if filtro != '*':
            if partes[indice_campo] == filtro:
                lineas_filtradas.append(linea.strip())
        else:
            lineas_filtradas.append(linea.strip())
