def check_void_parameter(variable, default_value):
    """
    Verifica si un parámetro tiene un valor asignado y, en caso contrario, le otorga el valor por defecto.
    :param variable: Requiere el parámetro que será evalaudo.
    :param default_value: Requiere el valor por defecto que se le asignará al parámetro si estuviera vacío.
    :return: Devuelve el parámetro con el valor que ingresó o con el valor por defecto asignado a él.
    """
    return default_value if variable is None else variable
