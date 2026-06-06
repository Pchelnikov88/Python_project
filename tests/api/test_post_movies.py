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

    def test_create_movie_minimal_fields(self, admin_api_manager: ApiManager):
        """Создание фильма только с обязательными полями"""
        unique_name = fake.unique.catch_phrase()

        movie_data = {
            "name": unique_name,
            "price": 100,
            "description": "Описание фильма",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

        response = admin_api_manager.movies_api.create_movie(movie_data)
        assert response.status_code == 201

        movie = response.json()
        assert movie["price"] == 100
        assert movie["description"] == "Описание фильма"
        assert movie["location"] == "MSK"
        assert movie["published"] is True
        assert movie["genreId"] == 1

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
    def test_create_movie_empty_name(self, admin_api_manager: ApiManager):
        """Создание фильма с пустым названием (ожидается ошибка 400)"""
        movie_data = {
            "name": "",
            "price": 200,
            "description": "Описание",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

        response = admin_api_manager.movies_api.create_movie(movie_data, expected_status=400)
        assert response.status_code == 400

        error = response.json()
        assert "message" in error

    def test_create_movie_duplicate_name(self, admin_api_manager: ApiManager):
        """Создание фильма только с обязательными полями"""

        movie_data = {
            "name": "Крестный отец",
            "price": 100,
            "description": "Описание фильма",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

        response = admin_api_manager.movies_api.create_movie(movie_data)
        assert response.status_code == 409, f'Ожидаем 409, получили {response.status_code}'

    def test_create_movie_duplicate_name(self, admin_api_manager: ApiManager):
        """Создание фильма с названием, которое уже существует (ожидается ошибка 409)"""
        from faker import Faker
        fake = Faker(locale='ru_RU')

        # 1. Создаем ПЕРВЫЙ фильм с уникальным названием
        unique_name = fake.unique.catch_phrase()

        first_movie_data = {
            "name": unique_name,
            "price": 200,
            "description": "Описание первого фильма",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

        response_first = admin_api_manager.movies_api.create_movie(first_movie_data)
        assert response_first.status_code == 201
        first_movie = response_first.json()

        # 2. Пытаемся создать ВТОРОЙ фильм с ТАКИМ ЖЕ названием
        second_movie_data = {
            "name": unique_name,
            "price": 300,
            "description": "Описание второго фильма",
            "location": "SPB",
            "published": False,
            "genreId": 2
        }

        response_second = admin_api_manager.movies_api.create_movie(second_movie_data, expected_status=409)

        # 3. Проверяем, что получили ошибку 409 Conflict
        assert response_second.status_code == 409

        error_data = response_second.json()
        assert "message" in error_data
        assert "Фильм с таким названием уже существует" in error_data["message"]
        assert error_data["statusCode"] == 409

    def test_create_movie_negative_price(self, admin_api_manager: ApiManager):
        """Создание фильма с отрицательной ценой (ожидается ошибка 400)"""
        movie_data = {
            "name": fake.catch_phrase(),
            "price": -100,
            "description": "Описание фильма",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

        response = admin_api_manager.movies_api.create_movie(movie_data, expected_status=400)
        assert response.status_code == 400

        error = response.json()
        assert "message" in error