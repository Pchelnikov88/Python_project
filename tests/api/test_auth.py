import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT,  LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api_classes.api_manager import ApiManager

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """Тест на регистрацию пользователя."""
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"



    # import pytest
# from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT
#
#
# class TestAuthAPI:
#     def test_register_user(self, requester, test_user):
#         """Тест на регистрацию пользователя."""
#         response = requester.send_request(
#             method="POST",
#             endpoint=REGISTER_ENDPOINT,
#             data=test_user,
#             expected_status=201
#         )
#         response_data = response.json()
#         assert response_data["email"] == test_user["email"], "Email не совпадает"
#         assert "id" in response_data, "ID пользователя отсутствует в ответе"
#         assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
#         assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"
#
#     def test_register_and_login_user(self, requester, registered_user):
#         """
#         Тест на регистрацию и авторизацию пользователя.
#         """
#         login_data = {
#             "email": registered_user["email"],
#             "password": registered_user["password"]
#         }
#         response = requester.send_request(
#             method="POST",
#             endpoint=LOGIN_ENDPOINT,
#             data=login_data,
#             expected_status=200
#         )
#         response_data = response.json()
#         assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
#         assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

# ======================== тесты до враппера =====================================================

# import pytest
# import requests
# from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
#
#
# class TestAuthAPI:
#     def test_register_user(self, test_user):
#         # URL для регистрации
#         register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
#
#         # Отправка запроса на регистрацию
#         response = requests.post(register_url, json=test_user, headers=HEADERS)
#
#         # Логируем ответ для диагностики
#         print(f"Response status: {response.status_code}")
#         print(f"Response body: {response.text}")
#
#         # Проверки
#         assert response.status_code == 201, "Ошибка регистрации пользователя"
#         response_data = response.json()
#         assert response_data["email"] == test_user["email"], "Email не совпадает"
#         assert "id" in response_data, "ID пользователя отсутствует в ответе"
#         assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
#
#         # Проверяем, что роль USER назначена по умолчанию
#         assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"
#
#     def test_login_user(self, test_user):
#         # URL для логина
#         login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
#
#         # пароль и логин
#         user_data = {
#             "email": test_user["email"],
#             "password": test_user["password"]
#         }
#
#         # отправим запрос на аутентификацию пользователя
#         login_response = requests.post(login_url, json=user_data, headers=HEADERS)
#
#         # получаем ответ
#         response_data = login_response.json()
#
#         # проверки
#         assert login_response.status_code == 200, "Аутентификация прошла не успешно"
#         assert "id" in response_data["user"], "В ответе отсутствует id"
#         assert test_user["email"] == response_data["user"]["email"], "email пользователя не совпадает"
#         assert test_user["fullName"] == response_data["user"]["fullName"], "fullName пользователя не совпадает"
#         assert response_data["user"]["roles"] == ["USER"], "Роль пользователя не совпадает"
#         assert "accessToken" in response_data, "В ответе отсутствует accessToken"
#         assert "refreshToken" in response_data, "В ответе отсутствует refreshToken"
#
#     def test_login_invalid_password(self, test_user):
#         # URL для логина
#         login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
#
#         # пароль и логин
#         user_data = {
#             "email": test_user["email"],
#             "password": "invalid_password"
#         }
#
#         # отправим запрос на аутентификацию пользователя
#         login_response = requests.post(login_url, json=user_data, headers=HEADERS)
#
#         # получаем ответ
#         response_data = login_response.json()
#
#         # проверки
#         assert login_response.status_code == 401, f"Ожидали 401, получили {login_response.status_code}"
#         assert response_data["message"] == "Неверный логин или пароль"
#
#     def test_login_invalid_email(self, test_user):
#         # URL для логина
#         login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
#
#         # пароль и логин
#         user_data = {
#             "email": "invalid_email@mail.ru",
#             "password": test_user["password"]
#         }
#
#         # отправим запрос на аутентификацию пользователя
#         login_response = requests.post(login_url, json=user_data, headers=HEADERS)
#
#         # получаем ответ
#         response_data = login_response.json()
#
#         # проверки
#         assert login_response.status_code == 401, f"Ожидали 401, получили {login_response.status_code}"
#         assert response_data["message"] == "Неверный логин или пароль"
#
#     def test_login_empty_body(self, test_user):
#         # URL для логина
#         login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
#
#         # пароль и логин
#         user_data = {}
#
#         # отправим запрос на аутентификацию пользователя
#         login_response = requests.post(login_url, json=user_data, headers=HEADERS)
#
#         # получаем ответ
#         response_data = login_response.json()
#
#         # проверки
#         assert login_response.status_code == 401, f"Ожидали 401, получили {login_response.status_code}"
#         assert response_data["message"] == "Неверный логин или пароль"