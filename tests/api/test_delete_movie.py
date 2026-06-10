# test_delete_movie.py pytest tests/api/test_delete_movie.py

from api_classes.api_manager import ApiManager
import pytest

class TestDeleteMovieAPI:
    """Тесты для удаления фильма DELETE /movies/{id}"""
    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
    def test_delete_movie_success(self, admin_api_manager: ApiManager, created_movie):
        """Успешное удаление существующего фильма"""
        # Фикстура created_movie создает фильм и возвращает его данные
        movie = created_movie()
        movie_id = movie["id"]

        # Удаляем фильм
        delete_response = admin_api_manager.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200

        # Проверяем, что фильм действительно удален
        get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert get_response.status_code == 404

    def test_delete_movie_returns_deleted_data(self, admin_api_manager: ApiManager, created_movie):
        """Проверка, что ответ содержит данные удаленного фильма"""
        # Создаем фильм с кастомными параметрами
        movie = created_movie(
            name="Фильм для проверки ответа",
            price=777,
            description="Проверяем тело ответа после удаления"
        )
        movie_id = movie["id"]

        # Удаляем фильм и проверяем тело ответа
        delete_response = admin_api_manager.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200

        deleted_movie = delete_response.json()
        assert deleted_movie["id"] == movie_id
        assert deleted_movie["name"] == "Фильм для проверки ответа"
        assert deleted_movie["price"] == 777
        assert deleted_movie["description"] == "Проверяем тело ответа после удаления"

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
    def test_delete_movie_not_found(self, admin_api_manager: ApiManager):
        """Удаление несуществующего фильма (ожидается ошибка 404)"""
        non_existent_id = 9999999

        response = admin_api_manager.movies_api.delete_movie(non_existent_id, expected_status=404)
        assert response.status_code == 404

        error = response.json()
        assert error["message"] == "Фильм не найден"
        assert error["error"] == "Not Found"
        assert error["statusCode"] == 404

    def test_delete_movie_twice(self, admin_api_manager: ApiManager, created_movie):
        """Повторное удаление одного и того же фильма (ожидается ошибка 404)"""
        # Создаем фильм через фикстуру
        movie = created_movie(name="Фильм для двойного удаления")
        movie_id = movie["id"]

        # Первое удаление - успешно
        delete_response_1 = admin_api_manager.movies_api.delete_movie(movie_id)
        assert delete_response_1.status_code == 200

        # Второе удаление - ошибка 404
        delete_response_2 = admin_api_manager.movies_api.delete_movie(movie_id, expected_status=404)
        assert delete_response_2.status_code == 404

    def test_delete_movie_invalid_id_zero(self, admin_api_manager: ApiManager):
        """Удаление фильма с ID = 0"""
        response = admin_api_manager.movies_api.delete_movie(0, expected_status=404)
        assert response.status_code == 404

    def test_delete_movie_invalid_id_negative(self, admin_api_manager: ApiManager):
        """Удаление фильма с отрицательным ID (ожидается ошибка 404)"""
        response = admin_api_manager.movies_api.delete_movie(-5, expected_status=404)
        assert response.status_code == 404

