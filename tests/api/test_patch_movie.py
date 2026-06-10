# test_patch_movie.py pytest tests/api/test_patch_movie.py

from api_classes.api_manager import ApiManager

class TestPatchMovieAPI:
    """Тесты для редактирования фильма PATCH /movies/{id}"""

    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
    def test_patch_movie_update_name(self, admin_api_manager: ApiManager, created_movie):
        """Успешное обновление названия фильма"""
        movie = created_movie()
        movie_id = movie["id"]
        new_name = f"Обновленное название {movie_id}"

        patch_response = admin_api_manager.movies_api.patch_movie(movie_id, {"name": new_name})
        assert patch_response.status_code == 200

        get_response = admin_api_manager.movies_api.get_movie_by_id(movie_id)
        assert get_response.status_code == 200
        updated_movie = get_response.json()

        assert updated_movie["name"] == new_name
        assert updated_movie["price"] == movie["price"]

    def test_patch_movie_verify_response(self, admin_api_manager: ApiManager, created_movie):
        """Проверка, что ответ после PATCH содержит обновленные данные"""
        movie = created_movie()
        movie_id = movie["id"]
        update_data = {"name": "Проверка ответа PATCH"}

        patch_response = admin_api_manager.movies_api.patch_movie(movie_id, update_data)
        assert patch_response.status_code == 200

        response_data = patch_response.json()
        assert response_data["name"] == update_data["name"]
        assert response_data["id"] == movie_id
        assert response_data["price"] == movie["price"]
        assert "createdAt" in response_data
        assert "rating" in response_data

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
    def test_patch_movie_not_found(self, admin_api_manager: ApiManager):
        """Редактирование несуществующего фильма (ожидается ошибка 404)"""
        non_existent_id = 9999999

        response = admin_api_manager.movies_api.patch_movie(
            non_existent_id,
            {"name": "Новое название"},
            expected_status=404
        )
        assert response.status_code == 404

        error = response.json()
        assert error["message"] == "Фильм не найден"
        assert error["statusCode"] == 404

    def test_patch_movie_invalid_id_zero(self, admin_api_manager: ApiManager):
        """Редактирование фильма с ID = 0 (ожидается ошибка 404)"""
        response = admin_api_manager.movies_api.patch_movie(0, {"name": "test"}, expected_status=404)
        assert response.status_code == 404

    def test_patch_movie_invalid_id_negative(self, admin_api_manager: ApiManager):
        """Редактирование фильма с отрицательным ID (ожидается ошибка 404)"""
        response = admin_api_manager.movies_api.patch_movie(-5, {"name": "test"}, expected_status=404)
        assert response.status_code == 404

