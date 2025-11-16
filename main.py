from src.api_module import get_companies, get_vacancies
from src.db_module import DBManager, save_data_to_db, create_database
from utils import user_interaction
import json


def main():
    """
    Основная функция для запуска программы.
    """
    db_name = 'hh_database'  # Имя вашей базы данных
    company_names = ["Яндекс", "Сбер", "Тинькофф", "VK", "Ozon", "Wildberries", "Альфа-Банк",
                     "Лаборатория Касперского", "Skyeng", "DataArt"]

    # 1. Создание базы данных
    create_database(db_name)

    # 2. Получение данных о компаниях и вакансиях с hh.ru
    companies = get_companies(company_names)

    all_vacancies = []
    for company in companies:
        vacancies = get_vacancies(company['id'])
        print(f"Компания {company['name']}: {len(vacancies)} вакансий")
        for vacancy in vacancies:
            vacancy['employer_name'] = company['name']  # Добавляем название компании к вакансии
        all_vacancies.extend(vacancies)

    print(f"Всего вакансий: {len(all_vacancies)}")

    # Сохранение полученных данных в файл (опционально, но полезно для отладки):
    with open("hh_data.json", "w", encoding="utf-8") as f:
        json.dump({"companies": companies, "vacancies": all_vacancies}, f, indent=4, ensure_ascii=False)

    # 3. Сохранение данных в базу данных
    save_data_to_db(companies, all_vacancies, db_name)

    # 4. Взаимодействие с пользователем через класс DBManager
    db_manager = DBManager(db_name)
    user_interaction(db_manager)


# Запускаем main, только если скрипт запускается напрямую
if __name__ == "__main__":
    main()
