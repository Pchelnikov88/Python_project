# test_get_movie.py pytest tests/api/test_get_movie.py

from api_classes.api_manager import ApiManager
from faker import Faker
import pytest

fake = Faker(locale='ru_RU')

class TestGetMoviesAPI:
    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
    def test_get_movie_by_id_success(self, admin_api_manager: ApiManager, created_movie):
        """Успешное получение существующего фильма по ID"""
        # 1. Создаем фильм через фикстуру
        movie = created_movie()
        movie_id = movie["id"]

        # 2. Получаем фильм по ID
        get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id)

        # 3. Проверки
        assert get_response.status_code == 200
        movie_data = get_response.json()

        assert movie_data["id"] == movie_id
        assert movie_data["name"] == movie["name"]
        assert movie_data["price"] == movie["price"]
        assert movie_data["description"] == movie["description"]
        assert movie_data["location"] == movie["location"]
        assert movie_data["published"] == movie["published"]
        assert movie_data["genreId"] == movie["genreId"]

        # Проверяем наличие дополнительных полей
        assert "createdAt" in movie_data
        assert "rating" in movie_data
        assert "genre" in movie_data
        assert "reviews" in movie_data
        assert isinstance(movie_data["reviews"], list)

    def test_get_movie_by_id_check_all_fields(self, admin_api_manager: ApiManager, api_manager: ApiManager, created_movie):
        """Проверка, что ответ содержит все необходимые поля"""
        # Создаем фильм (все поля генерируются автоматически)
        movie = created_movie()
        movie_id = movie["id"]

        # Получаем фильм по ID
        get_response = api_manager.movies_api.get_movie_by_id(movie_id)
        assert get_response.status_code == 200
        movie_data = get_response.json()

        # Проверяем наличие всех обязательных полей
        expected_fields = ["id", "name", "price", "description", "imageUrl",
                           "location", "published", "genreId", "genre", "createdAt", "rating", "reviews"]

        for field in expected_fields:
            assert field in movie_data, f"Поле '{field}' отсутствует в ответе"

        # Проверяем типы данных
        assert isinstance(movie_data["id"], int)
        assert isinstance(movie_data["name"], str)
        assert isinstance(movie_data["price"], int)
        assert isinstance(movie_data["description"], str)
        assert isinstance(movie_data["location"], str)
        assert isinstance(movie_data["published"], bool)
        assert isinstance(movie_data["genreId"], int)
        assert isinstance(movie_data["genre"], dict)
        assert isinstance(movie_data["createdAt"], str)
        assert isinstance(movie_data["rating"], int)
        assert isinstance(movie_data["reviews"], list)

        # Очистка
        admin_api_manager.movies_api.delete_movie(movie_id)

    def test_get_movie_by_id_verify_created_data(self, admin_api_manager: ApiManager, api_manager: ApiManager,
                                                 created_movie, custom_movie_data):
        """Проверка, что полученные данные соответствуют созданным (без авторизации)"""
        movie = created_movie(**custom_movie_data)
        movie_id = movie["id"]

        # Получаем фильм по ID
        get_response = api_manager.movies_api.get_movie_by_id(movie_id)
        assert get_response.status_code == 200
        movie_response = get_response.json()

        # Сравниваем все поля
        assert movie_response["name"] == custom_movie_data["name"]
        assert movie_response["price"] == custom_movie_data["price"]
        assert movie_response["description"] == custom_movie_data["description"]
        assert movie_response["location"] == custom_movie_data["location"]
        assert movie_response["published"] == custom_movie_data["published"]
        assert movie_response["genreId"] == custom_movie_data["genreId"]
        # Очистка
        admin_api_manager.movies_api.delete_movie(movie_id)

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
    def test_get_movie_by_id_not_found(self, api_manager: ApiManager):
        """Получение несуществующего фильма (ожидается ошибка 404)"""
        non_existent_id = 99999999

        response = api_manager.movies_api.get_movie_by_id(non_existent_id, expected_status=404)

        assert response.status_code == 404
        error = response.json()
        assert error["message"] == "Фильм не найден"
        assert error["error"] == "Not Found"
        assert error["statusCode"] == 404

    def test_get_movie_by_id_invalid_id_zero(self, api_manager: ApiManager):
        """Получение фильма с ID = 0 (ожидается ошибка 404) - без авторизации"""
        response = api_manager.movies_api.get_movie_by_id(0, expected_status=404)
        assert response.status_code == 404

    def test_get_movie_by_id_invalid_id_negative(self, api_manager: ApiManager):
        """Получение фильма с отрицательным ID (ожидается ошибка 404) - без авторизации"""
        response = api_manager.movies_api.get_movie_by_id(-1, expected_status=404)
        assert response.status_code == 404

    def test_get_movie_by_id_very_large_id(self, api_manager: ApiManager):
        """Получение фильма с очень большим ID (ожидается ошибка 404) - без авторизации"""
        huge_id = 9999999999999999999999
        response = api_manager.movies_api.get_movie_by_id(huge_id, expected_status=500)
        assert response.status_code == 500