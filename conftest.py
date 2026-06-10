# conftest.py

from faker import Faker
import pytest
import requests
import random
from constants import BASE_URL, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from api_classes.api_manager import ApiManager


faker = Faker()

fake = Faker(locale='ru_RU')
cities = ["SPB", "MSK"]
SORT_OPTIONS = ["asc", "desc"]

@pytest.fixture
def movies_filter_params():
    """Фикстура с параметрами для фильтрации фильмов"""
    return {
        "page": fake.random_int(min=1, max=10),
        "pageSize": fake.random_int(min=5, max=20),
        "minPrice": fake.random_int(min=1, max=500),
        "maxPrice": fake.random_int(min=100, max=1000),
        "locations": random.choice(cities),
        "published": fake.boolean(),
        "genreId": fake.random_int(min=1, max=10),
        "createdAt": random.choice(SORT_OPTIONS)
    }

@pytest.fixture(scope="function")
def creation_movies_list():
    """Фикстура для генерации тестовых данных фильма."""
    return {
        "name": fake.catch_phrase(),
        "price": fake.random_int(min=100, max=500),
        "description": fake.text(max_nb_chars=200),
        "location": random.choice(cities),
        "published": fake.boolean(),
        "genreId": fake.random_int(min=1, max=5)
    }

@pytest.fixture
def custom_movie_data():
    """Фикстура с тестовыми данными для фильма"""
    return {
        "name": "Проверка соответствия данных-1",
        "price": 500,
        "description": "Длинное описание фильма для проверки соответствия данных",
        "location": "SPB",
        "published": False,
        "genreId": 3
    }

# @pytest.fixture(scope="session")
# def params_():
#     """Валидные данные для поиска фильмов"""
#     return  {
#         "pageSize": 10,
#         "page": 1,
#         "minPrice": 300,
#         "maxPrice": 500,
#         "locations": "MSK",
#         "published": True,
#         "createdAt": "asc"
#     }

@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    Гарантирует, что сессия будет корректно
    закрыта после завершения всех тестов.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="function")
def created_movie(api_manager):
    """
    Фикстура для создания фильма через API.
    Возвращает данные созданного фильма.
    Фильм автоматически удаляется после теста.
    """
    created_movies = []  # список созданных фильмов для очистки

    def _create_movie(**kwargs):
        # Базовые данные фильма
        movie_data = {
            "name": fake.catch_phrase(),
            "price": fake.random_int(min=100, max=500),
            "description": fake.text(max_nb_chars=200),
            "location": random.choice(cities),
            "published": fake.boolean(),
            "genreId": fake.random_int(min=1, max=5),
            "imageUrl": fake.image_url()
        }
        # Переопределяем переданными параметрами
        movie_data.update(kwargs)

        # Создаем фильм
        response = api_manager.movies_api.create_movie(movie_data)
        assert response.status_code == 201, f"Фильм не создан. Статус: {response.status_code}"

        created_movie_data = response.json()
        created_movies.append(created_movie_data)  # запоминаем для очистки
        return created_movie_data

    yield _create_movie

    # Очистка после теста: удаляем все созданные фильмы
    for movie in created_movies:
        try:
            api_manager.movies_api.delete_movie(movie["id"])  # ← ожидает 200 (по умолчанию)
        except Exception as e:
            print(f"Не удалось удалить фильм {movie['id']}: {e}")


@pytest.fixture(scope="session")
def admin_api_manager(api_manager: ApiManager):
    """
    Фикстура, которая авторизуется как ADMIN и возвращает ApiManager
    с уже настроенными заголовками авторизации.
    """
    # 1. Данные админа
    admin_creds = ("api1@gmail.com", "asdqwe123Q")

    # 2. Выполняем логин и обновляем заголовки сессии
    #    Метод authenticate сам установит заголовок Authorization
    api_manager.auth_api.authenticate(admin_creds)

    # 3. Возвращаем настроенный api_manager
    return api_manager

#==================================================== до реквестера
# import requests
# from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
# import pytest
# from utils.data_generator import DataGenerator
#
# @pytest.fixture(scope="session")
# def test_user():
#     """Генерация случайного пользователя для тестов"""
#
#     random_email = DataGenerator.generate_random_email()
#     random_name = DataGenerator.generate_random_name()
#     random_password = DataGenerator.generate_random_password()
#
#     return {
#         "email": random_email,
#         "fullName": random_name,
#         "password": random_password,
#         "passwordRepeat": random_password,
#         "roles": ["USER"]
#     }
#
#
# @pytest.fixture(scope="session")
# def auth_session(test_user):
#     # Регистрируем нового пользователя
#     register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
#     response = requests.post(register_url, json=test_user, headers=HEADERS)
#     assert response.status_code == 201, "Ошибка регистрации пользователя"
#
#     # Логинимся для получения токена
#     login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
#     login_data = {
#         "email": test_user["email"],
#         "password": test_user["password"]
#     }
#     response = requests.post(login_url, json=login_data, headers=HEADERS)
#     assert response.status_code == 200, "Ошибка авторизации"
#
#     # Получаем токен и создаём сессию
#     token = response.json().get("accessToken")
#     assert token is not None, "Токен доступа отсутствует в ответе"
#
#     session = requests.Session()
#     session.headers.update(HEADERS)
#     session.headers.update({"Authorization": f"Bearer {token}"})
#     return session