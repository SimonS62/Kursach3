import requests
from typing import List, Dict


def get_companies(company_names: List[str]) -> List[Dict]:
    """
    Получает данные о компаниях по списку их названий.
    """
    companies = []
    for name in company_names:
        url = f"https://api.hh.ru/employers?text={name}&only_with_vacancies=true"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['items']:  # убедимся, что что-то вернулось
                companies.extend(data['items'])  # Добавляем все найденные элементы
        else:
            print(f"Ошибка при получении данных о компании {name}: {response.status_code}")
    return companies


def get_vacancies(employer_id: int) -> List[Dict]:
    """
    Получает данные о вакансиях компании по её ID.
    """
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}"
    vacancies = []
    page = 0
    while True:
        url_with_page = f"{url}&page={page}"
        response = requests.get(url_with_page)
        if response.status_code == 200:
            data = response.json()
            vacancies.extend(data['items'])
            if data['pages'] - 1 <= page:  # проверяем, есть ли еще страницы
                break
            page += 1
        else:
            print(f"Ошибка при получении вакансий компании {employer_id}: {response.status_code}")
            break
    return vacancies
