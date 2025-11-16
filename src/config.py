from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    """
    Читает параметры подключения к БД из файла database.ini.
    """
    # создаем парсер
    parser = ConfigParser()
    # читаем файл конфигурации
    parser.read(filename)

    # получаем секцию, по умолчанию "postgresql"
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} не найден в файле {1}'.format(section, filename))

    return db
