# test_post_movies pytest tests/api/test_post_movies.py

import pytest
from faker import Faker
from api_classes.api_manager import ApiManager

fake = Faker(locale='ru_RU')

class TestPostMoviesAPI:
    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
    def test_create_movie_success(self, admin_api_manager: ApiManager, creation_movies_list):
        """Успешное создание фильма с валидными данными"""
        response = admin_api_manager.movies_api.create_movie(creation_movies_list)

        assert response.status_code == 201
        movie_data = response.json()

        # Проверяем структуру ответа
        assert "id" in movie_data, "Ответ должен содержать id фильма"
        assert movie_data["name"] == creation_movies_list["name"], "Название не совпадает"
        assert movie_data["price"] == creation_movies_list["price"], "Цена не совпадает"
        assert movie_data["description"] == creation_movies_list["description"], "Описание не совпадает"
        assert movie_data["location"] == creation_movies_list["location"], "Локация не совпадает"
        assert movie_data["published"] == creation_movies_list["published"], "Статус публикации не совпадает"
        assert movie_data["genreId"] == creation_movies_list["genreId"], "ID жанра не совпадает"

        # Проверяем дополнительные поля
        assert "createdAt" in movie_data, "Должна быть дата создания"
        assert "rating" in movie_data, "Должен быть рейтинг"
        assert movie_data["rating"] == 0, "У нового фильма рейтинг должен быть 0"

    def test_get_movie_by_id_verify_created_data(self, admin_api_manager: ApiManager, api_manager: ApiManager, created_movie, custom_movie_data):
        """Проверка, что полученные данные соответствуют созданным (без авторизации)"""
        # Создаем фильм с данными из фикстуры
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

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
    def test_create_movie_empty_name(self, admin_api_manager: ApiManager, custom_movie_data):
        """Создание фильма с пустым названием (ожидается ошибка 400)"""
        # Берем данные из фикстуры и переопределяем name
        movie_data = custom_movie_data.copy()
        movie_data["name"] = ""

        response = admin_api_manager.movies_api.create_movie(movie_data, expected_status=400)
        assert response.status_code == 400

        error = response.json()
        assert "message" in error

    def test_create_movie_duplicate_name(self, admin_api_manager: ApiManager, custom_movie_data):
        """Создание фильма с названием, которое уже существует (ожидается ошибка 409)"""
        # Создаем первый фильм
        unique_name = fake.unique.catch_phrase()
        first_movie_data = custom_movie_data.copy()
        first_movie_data["name"] = unique_name

        response_first = admin_api_manager.movies_api.create_movie(first_movie_data)
        assert response_first.status_code == 201
        first_movie = response_first.json()

        # Пытаемся создать второй фильм с тем же названием
        second_movie_data = custom_movie_data.copy()
        second_movie_data["name"] = unique_name

        response_second = admin_api_manager.movies_api.create_movie(second_movie_data, expected_status=409)
        assert response_second.status_code == 409

        error_data = response_second.json()
        assert "message" in error_data
        assert "Фильм с таким названием уже существует" in error_data["message"]
        assert error_data["statusCode"] == 409

        # Очистка
        admin_api_manager.movies_api.delete_movie(first_movie["id"])

    def test_create_movie_negative_price(self, admin_api_manager: ApiManager, custom_movie_data):
        """Создание фильма с отрицательной ценой (ожидается ошибка 400)"""
        # Берем данные из фикстуры и меняем цену
        movie_data = custom_movie_data.copy()
        movie_data["price"] = -100

        response = admin_api_manager.movies_api.create_movie(movie_data, expected_status=400)
        assert response.status_code == 400

        error = response.json()
        assert "message" in error