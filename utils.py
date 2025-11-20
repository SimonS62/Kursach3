from db_module import DBManager

def user_interaction(db_manager: DBManager) -> None:
    """
    Осуществляет взаимодействие с пользователем, предоставляя возможности работы с базой данных.

    Args:
        db_manager: Экземпляр класса DBManager для работы с базой данных.
    """
    while True:
        print("\nВыберите действие:")
        print("1 - Получить список компаний и количество вакансий у каждой компании")
        print("2 - Получить список всех вакансий")
        print("3 - Получить среднюю зарплату по вакансиям")
        print("4 - Получить список вакансий с зарплатой выше средней")
        print("5 - Получить список вакансий, содержащих ключевое слово")
        print("0 - Выход")

        choice = input("Ваш выбор: ")

        if choice == '1':
            companies_vacancies = db_manager.get_companies_and_vacancies_count()
            if companies_vacancies:
                print("\nКомпании и количество вакансий:")
                for company, count in companies_vacancies:
                    print(f"{company}: {count}")
            else:
                print("Нет данных о компаниях и вакансиях.")

        elif choice == '2':
            all_vacancies = db_manager.get_all_vacancies()
            if all_vacancies:
                print("\nВсе вакансии:")
                for company, title, salary_from, salary_to, url in all_vacancies:
                    print(f"{company}: {title}, Зарплата: от {salary_from} до {salary_to}, URL: {url}")
            else:
                print("Нет данных о вакансиях.")

        elif choice == '3':
            avg_salary = db_manager.get_avg_salary()
            if avg_salary is not None:
                print(f"\nСредняя зарплата: {avg_salary}")
            else:
                print("Нет данных о зарплатах для вычисления средней зарплаты.")

        elif choice == '4':
            higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
            if higher_salary_vacancies:
                print("\nВакансии с зарплатой выше средней:")
                for title, salary_from, salary_to, url in higher_salary_vacancies:
                    print(f"{title}, Зарплата: от {salary_from} до {salary_to}, URL: {url}")
            else:
                print("Нет вакансий с зарплатой выше средней.")

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска вакансий: ")
            keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            if keyword_vacancies:
                print(f"\nВакансии с ключевым словом '{keyword}':")
                for title, salary_from, salary_to, url in keyword_vacancies:
                    print(f"{title}, Зарплата: от {salary_from} до {salary_to}, URL: {url}")
            else:
                print(f"Нет вакансий, содержащих ключевое слово '{keyword}'.")

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите действие из списка.")
