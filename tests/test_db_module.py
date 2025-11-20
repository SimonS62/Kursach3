import unittest
from unittest.mock import patch, MagicMock
import psycopg2
from src.config import config
from src.db_module import DBManager, create_database, create_tables
from typing import List, Tuple, Optional


class TestDBManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Sets up a test database for all tests in this class."""
        cls.test_db_name = f"test_db_{uuid.uuid4().hex}"  # Уникальное имя БД для каждого тестового запуска
        create_database(cls.test_db_name)  # Используем вашу функцию для её создания.
        # Теперь создаем подключение, которое будем использовать для дальнейших операций setUp
        cls.test_db_params = config()
        cls.test_db_params['database'] = cls.test_db_name
        cls.conn = psycopg2.connect(**cls.test_db_params)
        create_tables(cls.conn)  #  и таблицы в тестовой базе данных

        # Заполняем тестовую БД данными
        with cls.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO employers (name, url, hh_id) VALUES
                ('Employer A', 'http://example.com/a', 1),
                ('Employer B', 'http://example.com/b', 2);

                INSERT INTO vacancies (employer_id, title, salary_from, salary_to, url, employer_name) VALUES
                (1, 'Vacancy 1', 50000, 70000, 'http://example.com/v1', 'Employer A'),
                (1, 'Vacancy 2', 60000, 80000, 'http://example.com/v2', 'Employer A'),
                (2, 'Vacancy 3', 70000, 90000, 'http://example.com/v3', 'Employer B'),
                (2, 'Vacancy 4', 80000, 100000, 'http://example.com/v4', 'Employer B'),
                (2, 'Vacancy 5', None, None, 'http://example.com/v5', 'Employer B');
            """)
        cls.conn.commit()


    @classmethod
    def tearDownClass(cls):
        """Tears down the test database after all tests have run."""
        # Закрываем соединение перед удалением БД
        cls.conn.close()

        # Удаляем тестовую базу данных.  Это важно, чтобы не засорять окружение.
        test_db_params_cleanup = config(section='postgresql')  # Подключаемся БЕЗ указания БД
        conn_cleanup = None
        try:
            conn_cleanup = psycopg2.connect(**test_db_params_cleanup)
            conn_cleanup.autocommit = True  # Важно для DDL команд
            cursor_cleanup = conn_cleanup.cursor()
            cursor_cleanup.execute(f"DROP DATABASE IF EXISTS {cls.test_db_name}")

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error dropping database:", error)
        finally:
            if conn_cleanup is not None:
                cursor_cleanup.close()
                conn_cleanup.close()



    def setUp(self):
       """Creates a DBManager instance before each test."""
       self.db_manager = DBManager(self.test_db_name)
       # self.mock_conn = MagicMock()  # больше не нужно
       # self.db_manager.get_connection = MagicMock(return_value=self.mock_conn)



    def test_get_companies_and_vacancies_count(self):
        """Tests the get_companies_and_vacancies_count method."""
        expected_result = [('Employer B', 3), ('Employer A', 2)]
        actual_result = self.db_manager.get_companies_and_vacancies_count()
        self.assertEqual(actual_result, expected_result)

    def test_get_all_vacancies(self):
        """Tests the get_all_vacancies method."""
        expected_result = [
            ('Employer A', 'Vacancy 1', 50000, 70000, 'http://example.com/v1'),
            ('Employer A', 'Vacancy 2', 60000, 80000, 'http://example.com/v2'),
            ('Employer B', 'Vacancy 3', 70000, 90000, 'http://example.com/v3'),
            ('Employer B', 'Vacancy 4', 80000, 100000, 'http://example.com/v4'),
            ('Employer B', 'Vacancy 5', None, None, 'http://example.com/v5')
        ]  # Проверьте порядок вакансий, если это важно!
        actual_result = self.db_manager.get_all_vacancies()
        self.assertEqual(actual_result, expected_result)



    def test_get_avg_salary(self):
        """Tests the get_avg_salary method."""
        expected_result = 75000.0
        actual_result = self.db_manager.get_avg_salary()
        self.assertEqual(actual_result, expected_result)

    def test_get_vacancies_with_higher_salary(self):
        """Tests the get_vacancies_with_higher_salary method."""
        expected_result = [
            ('Vacancy 3', 70000, 90000, 'http://example.com/v3'),
            ('Vacancy 4', 80000, 100000, 'http://example.com/v4')
        ]  # Проверьте порядок вакансий!
        actual_result = self.db_manager.get_vacancies_with_higher_salary()
        self.assertEqual(actual_result, expected_result)

    def test_get_vacancies_with_keyword(self):
        """Tests the get_vacancies_with_keyword method."""
        expected_result = [('Vacancy 1', 50000, 70000, 'http://example.com/v1')]
        actual_result = self.db_manager.get_vacancies_with_keyword('1')
        self.assertEqual(actual_result, expected_result)

    def test_get_vacancies_with_keyword_no_match(self):
        """Tests the get_vacancies_with_keyword method when no match is found."""
        expected_result: List[Tuple[str, Optional[int], Optional[int], str]] = []
        actual_result = self.db_manager.get_vacancies_with_keyword('NonExistentKeyword')
        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    unittest.main()
