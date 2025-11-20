import pytest
from unittest.mock import patch
from src.api_module import get_companies, get_vacancies

@pytest.fixture
def mock_response():
    """Фикстура для создания Mock-объекта ответа requests."""
    def _mock_response(status_code: int, json_:

    @patch('src.api_module.requests.get')  # Patch для функции requests.get
    def test_get_companies_success(self, mock_get, mock_response):
        """Успешное получение данных о компаниях."""
        company_names = ["Яндекс", "Google"]
        expected_companies = [{"id": "123", "name": "Яндекс"}, {"id": "456", "name": "Google"}]
        mock_get.side_effect = [
            mock_response(200, {"items": [expected_companies[0]]}),
            mock_response(200, {"items": [expected_companies[1]]})
        ]

        companies = get_companies(company_names)
        assert len(companies) == 2
        assert companies == expected_companies

    @patch('src.api_module.requests.get')
    def test_get_companies_no_data(self, mock_get, mock_response):
        """Когда API не возвращает данные (пустой список items)."""
        company_names = ["NonExistentCompany"]
        mock_get.return_value = mock_response(200, {"items": []})

        companies = get_companies(company_names)
        assert len(companies) == 0

    @patch('src.api_module.requests.get')
    def test_get_companies_api_error(self, mock_get, mock_response):
        """Обработка ошибки API."""
        company_names = ["CompanyWithError"]
        mock_get.return_value = mock_response(500, {})  # Симулируем ошибку 500

        companies = get_companies(company_names)
        assert len(companies) == 0  # Ожидаем пустой список в случае ошибки


class TestGetVacancies:

    @patch('src.api_module.requests.get')
    def test_get_vacancies_success_single_page(self, mock_get, mock_response):
        """Успешное получение вакансий с одной страницы."""
        employer_id = 123
        expected_vacancies = [{"id": "789", "name": "Вакансия 1"}, {"id": "101", "name": "Вакансия 2"}]
        mock_get.return_value = mock_response(200, {"items": expected_vacancies, "pages": 1})

        vacancies = get_vacancies(employer_id)
        assert len(vacancies) == 2
        assert vacancies == expected_vacancies

    @patch('src.api_module.requests.get')
    def test_get_vacancies_success_multiple_pages(self, mock_get, mock_response):
        """Успешное получение вакансий с нескольких страниц."""
        employer_id = 123
        page1_vacancies = [{"id": "1", "name": "Вакансия 1"}, {"id": "2", "name": "Вакансия 2"}]
        page2_vacancies = [{"id": "3", "name": "Вакансия 3"}, {"id": "4", "name": "Вакансия 4"}]

        mock_get.side_effect = [
            mock_response(200, {"items": page1_vacancies, "pages": 2}),
            mock_response(200, {"items": page2_vacancies, "pages": 2})
        ]

        vacancies = get_vacancies(employer_id)
        assert len(vacancies) == 4
        assert vacancies == page1_vacancies + page2_vacancies

    @patch('src.api_module.requests.get')
    def test_get_vacancies_api_error(self, mock_get, mock_response):
        """Обработка ошибки API при получении вакансий."""
        employer_id = 123
        mock_get.return_value = mock_response(500, {})

        vacancies = get_vacancies(employer_id)
        assert len(vacancies) == 0

    @patch('src.api_module.requests.get')
    def test_get_vacancies_empty_response(self, mock_get, mock_response):
          """Обработка ситуации, когда API возвращает пустой ответ (нет вакансий)."""
          employer_id = 123
          mock_get.return_value = mock_response(200, {"items": [], "pages": 0}) # Нет вакансий, 0 страниц

          vacancies = get_vacancies(employer_id)
          assert len(vacancies) == 0
