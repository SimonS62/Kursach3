import psycopg2
from config import config
from typing import List, Tuple, Optional


class DBManager:
    """
    Класс для управления данными в БД PostgreSQL.
    """

    def __init__(self, database_name: str):
        """
        Инициализирует объект DBManager.

        Args:
            database_name: Имя базы данных.
        """
        self.database_name = database_name
        self.params = config()
        self.params['database'] = database_name  # Добавляем имя БД в параметры

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            Список кортежей, где первый элемент - название компании, второй - количество вакансий.
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.name, COUNT(v.vacancy_id)
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
                ORDER BY COUNT(v.vacancy_id) DESC
            """)
            result = cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in get_companies_and_vacancies_count", error)
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.

        Returns:
            Список кортежей, где:
              - первый элемент - название компании,
              - второй - название вакансии,
              - третий - зарплата "от" (может быть None),
              - четвертый - зарплата "до" (может быть None),
              - пятый - ссылка на вакансию.
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
            """)
            result = cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in get_all_vacancies", error)
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            Средняя зарплата (может быть None, если нет данных).
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT AVG((salary_from + salary_to) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
            """)
            result = cursor.fetchone()[0]
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in get_avg_salary", error)
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, Optional[int], Optional[int], str]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            Список кортежей, где:
              - первый элемент - название вакансии,
              - второй - зарплата "от" (может быть None),
              - третий - зарплата "до" (может быть None),
              - четвертый - ссылка на вакансию.
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT title, salary_from, salary_to, url
                FROM vacancies
                WHERE (salary_from + salary_to) / 2 > (SELECT AVG((salary_from + salary_to) / 2) FROM vacancies WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL)
                AND salary_from IS NOT NULL AND salary_to IS NOT NULL
            """)
            result = cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in get_vacancies_with_higher_salary", error)
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, Optional[int], Optional[int], str]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.

        Args:
            keyword: Слово для поиска в названии вакансии.

        Returns:
            Список кортежей, где:
              - первый элемент - название вакансии,
              - второй - зарплата "от" (может быть None),
              - третий - зарплата "до" (может быть None),
              - четвертый - ссылка на вакансию.
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT title, salary_from, salary_to, url
                FROM vacancies
                WHERE title LIKE %s
                """,
                ('%' + keyword + '%',)  # Важно: передаем keyword как кортеж!
            )
            result = cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in get_vacancies_with_keyword", error)
        finally:
            if conn is not None:
                cursor.close()
                conn.close()


def create_database(db_name: str) -> None:
    """Создает базу данных, если она не существует."""
    params = config(section='postgresql')  # Получаем параметры подключения без указания БД
    conn = None
    try:
        # Подключаемся к PostgreSQL (без указания конкретной базы данных)
        conn = psycopg2.connect(**params)
        conn.autocommit = True  # Важно: необходимо установить autocommit в True для выполнения DDL команд
        cursor = conn.cursor()

        # Проверяем, существует ли база данных
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cursor.fetchone()
        if not exists:
            # Создаем базу данных
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating database:", error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            print("Connection closed.")


def create_tables(conn: psycopg2.extensions.connection) -> None:
    """Создает таблицы в БД, если их нет."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            employer_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            hh_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id SERIAL PRIMARY KEY,
            employer_id INTEGER REFERENCES employers(employer_id),
            title VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            currency VARCHAR(50),
            url VARCHAR(255) NOT NULL,
            description TEXT,
            employer_name VARCHAR(255)
        );
    """)
    conn.commit()


def save_data_to_db(companies: List[Dict], all_vacancies: List[Dict], database_name: str) -> None:
    """Сохраняет данные о компаниях и вакансиях в БД."""
    params = config()
    params['database'] = database_name  # Указываем имя базы данных
    conn = None
    try:
        # Подключение к БД
        conn = psycopg2.connect(**params)
        conn.autocommit = False  # выключаем autocommit, чтобы можно было откатить изменения в случае ошибки
        cursor = conn.cursor()

        create_tables(conn)  # Создаем таблицы, если их нет

        # Заполнение таблицы employers
        for company in companies:
            cursor.execute(
                """
                INSERT INTO employers (name, url, hh_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (hh_id) DO NOTHING  -- Предотвращаем дублирование
                RETURNING employer_id
                """,
                (company['name'], company['alternate_url'], company['id'])  # 'alternate_url' вместо 'url'
            )
            conn.commit() #  коммитим после каждой вставки компании
            employer_id = cursor.fetchone()[0]

            # Заполнение таблицы vacancies
            for vacancy in all_vacancies:
                if vacancy['employer']['id'] == company['id']:  # Сравниваем ID, а не имя

                    # Обработка зарплаты (может быть None)

                    salary_from = None
                    salary_to = None
                    currency = None

                    if vacancy.get('salary'):
                        salary_from = vacancy['salary'].get('from')
                        salary_to = vacancy['salary'].get('to')
                        currency = vacancy['salary'].get('currency')
                        # print(f"Vacancy: {vacancy['name']}, Salary From: {salary_from}, Salary To: {salary_to}, Currency: {currency}")
                        # else:
                        #     print(f"Vacancy: {vacancy['name']}, Salary is None")

                    cursor.execute(
                        """
                        INSERT INTO vacancies (employer_id, title, salary_from, salary_to, currency, url, description, employer_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (employer_id, vacancy['name'], salary_from, salary_to, currency, vacancy['alternate_url'],
                         vacancy.get('snippet').get('requirement') if vacancy.get('snippet') else None,
                         company['name'])
                    )
                    conn.commit() # коммитим после каждой вставки вакансии

        conn.commit() #  окончательно коммитим изменения
        print("Данные успешно сохранены в БД.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Ошибка при работе с PostgreSQL", error)
        if conn is not None:
            conn.rollback() # откатываем изменения в случае ошибки
        print("Изменения отменены.")
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            print("Соединение с БД закрыто")
