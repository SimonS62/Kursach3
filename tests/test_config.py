import unittest
from unittest.mock import patch, mock_open
from src.config import config


# Ваша функция config (убедитесь, что она находится в отдельном модуле, например, 'database_config.py')
from database_config import config  # Замените 'database_config' на имя вашего модуля

class TestConfig(unittest.TestCase):

    def test_config_valid_section(self):
        # Mock файла database.ini с валидными данными
        config_data = """
        [postgresql]
        host=localhost
        database=mydatabase
        user=myuser
        password=mypassword
        port=5432
        """

        with patch('builtins.open', mock_open(read_data=config_data)):
            db_config = config(filename='database.ini', section='postgresql')
            self.assertEqual(db_config['host'], 'localhost')
            self.assertEqual(db_config['database'], 'mydatabase')
            self.assertEqual(db_config['user'], 'myuser')
            self.assertEqual(db_config['password'], 'mypassword')
            self.assertEqual(db_config['port'], '5432')

    def test_config_default_section(self):
        # Mock файла database.ini с дефолтной секцией
        config_data = """
        [postgresql]
        host=localhost
        database=mydatabase
        """
        with patch('builtins.open', mock_open(read_data=config_data)):
            db_config = config(filename='database.ini') # Опускаем section, должен работать дефолт
            self.assertEqual(db_config['host'], 'localhost')
            self.assertEqual(db_config['database'], 'mydatabase')


    def test_config_invalid_section(self):
        # Mock файла database.ini без нужной секции
        config_data = """
        [mysql]
        host=localhost
        database=mydatabase
        """
        with patch('builtins.open', mock_open(read_data=config_data)):
            with self.assertRaises(Exception) as context:
                config(filename='database.ini', section='postgresql')  # Попытка чтения несуществующей секции

            self.assertTrue('Section postgresql не найден в файле database.ini' in str(context.exception))


    def test_config_file_not_found(self):
        # Проверка случая, когда файл конфигурации не найден.
        # В данном случае, проще просто не мокать файл,  и assertRaises должен сработать.
        with self.assertRaises(FileNotFoundError):
            config(filename='nonexistent_file.ini')



if __name__ == '__main__':
    unittest.main()
