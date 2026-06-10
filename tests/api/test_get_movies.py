# test_get_movies.py pytest tests/api/test_get_movies.py

from api_classes.api_manager import ApiManager

class TestGetMoviesAPI:
    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
    def test_get_movies_with_filters(self, api_manager: ApiManager, movies_filter_params):
        """Успешное получение фильмов по валидным данным"""
        response = api_manager.movies_api.get_movies(params=movies_filter_params)

        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

        # проверяем что JSON валидный
        try:
            data = response.json()
        except Exception as e:
            assert False, f"Ответ не является валидным JSON: {e}"

        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"
        assert "count" in data, "Ответ должен содержать поле 'count'"
        assert "page" in data, "Ответ должен содержать поле 'page'"
        assert "pageSize" in data, "Ответ должен содержать поле 'pageSize'"
        assert "pageCount" in data, "Ответ должен содержать поле 'pageCount'"

        movies = data.get("movies", [])
        assert isinstance(movies, list), "movies должен быть списком"

    def test_get_movies_no_filters(self, api_manager: ApiManager):
        """Успешное получение фильмов без фильтров"""
        response = api_manager.movies_api.get_movies()

        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

        # проверяем что JSON валидный
        try:
            data = response.json()
        except Exception as e:
            assert False, f"Ответ не является валидным JSON: {e}"

    def test_get_movies_pagination_page_size(self, api_manager: ApiManager):
        """Проверка, что pageSize ограничивает количество фильмов"""
        page_size = 5
        params = {"page": 1, "pageSize": page_size}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

        data = response.json()
        # Проверяем, что в ответе есть поле movies
        assert "movies" in data, "В ответе отсутствует поле 'movies'"

        movies = data.get("movies", [])
        assert len(movies) <= page_size, \
            f"Получено {len(movies)} фильмов, должно быть не более {page_size}"

        # Дополнительная проверка: pageSize в ответе соответствует запрошенному
        assert data.get("pageSize") == page_size, \
            f"pageSize в ответе {data.get('pageSize')} не соответствует запрошенному {page_size}"

    def test_get_movies_pagination_first_page(self, api_manager: ApiManager):
        """Проверка получения первой страницы"""
        params = {"page": 1, "pageSize": 10}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

    def test_get_movies_pagination_second_page(self, api_manager: ApiManager):
        """Проверка, что страницы не повторяются"""
        params_page1 = {"page": 1, "pageSize": 5}
        params_page2 = {"page": 2, "pageSize": 5}

        response1 = api_manager.movies_api.get_movies(params=params_page1)
        response2 = api_manager.movies_api.get_movies(params=params_page2)

        assert response1.status_code == 200, f'Ожидали 200, получили {response1.status_code}'
        assert response2.status_code == 200, f'Ожидали 200, получили {response2.status_code}'

        data1 = response1.json()
        data2 = response2.json()

        movies1 = data1.get("movies", [])
        movies2 = data2.get("movies", [])

        # ID фильмов на разных страницах не должны совпадать
        if len(movies1) > 0 and len(movies2) > 0:
            ids1 = [movie["id"] for movie in movies1]
            ids2 = [movie["id"] for movie in movies2]
            assert set(ids1).isdisjoint(set(ids2)), "Фильмы не должны повторяться между страницами"

    def test_get_movies_filter_by_location_msk(self, api_manager: ApiManager):
        """Проверка фильтрации по локации (Москва)"""
        params = {"locations": ["MSK"]}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

        data = response.json()

        # Получаем массив фильмов из поля "movies"
        movies = data.get("movies", [])

        # Проверяем, что все фильмы в Москве
        for movie in movies:
            assert movie["location"] == "MSK", f"Фильм должен быть в MSK, а он в {movie['location']}"

    def test_get_movies_filter_by_price_range(self, api_manager: ApiManager):
        """Проверка фильтрации по диапазону цен"""
        params = {"minPrice": 100, "maxPrice": 300}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200, f'Ожидали 200, получили {response.status_code}'

        data = response.json()
        movies = data.get("movies", [])

        for movie in movies:
            assert 100 <= movie["price"] <= 300, f"Цена {movie['price']} вне диапазона 100-300"

    def test_get_movies_published_only(self, api_manager: ApiManager):
        """Проверка получения только опубликованных фильмов"""
        params = {"published": True}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200

        data = response.json()
        movies = data.get("movies", [])

        for movie in movies:
            assert movie["published"] is True, "Фильм должен быть опубликован"

    def test_get_movies_filter_by_genre(self, api_manager: ApiManager):
        """Проверка фильтрации по жанру"""
        params = {"genreId": 3}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200

        data = response.json()
        movies = data.get("movies", [])

        for movie in movies:
            assert movie["genreId"] == 3, f"Жанр должен быть 3, а получен {movie['genreId']}"

    def test_get_movies_sort_by_created_at_asc(self, api_manager: ApiManager):
        """Проверка сортировки по дате создания (по возрастанию)"""
        params = {"createdAt": "asc"}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200

        data = response.json()
        movies = data.get("movies", [])

        if len(movies) > 1:
            dates = [movie["createdAt"] for movie in movies]
            assert dates == sorted(dates), "Даты должны идти по возрастанию"

    def test_get_movies_sort_by_created_at_desc(self, api_manager: ApiManager):
        """Проверка сортировки по дате создания (по убыванию)"""
        params = {"createdAt": "desc"}

        response = api_manager.movies_api.get_movies(params=params)
        assert response.status_code == 200

        data = response.json()
        movies = data.get("movies", [])

        if len(movies) > 1:
            dates = [movie["createdAt"] for movie in movies]
            assert dates == sorted(dates, reverse=True), "Даты должны идти по убыванию"

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================

    def test_get_movies_invalid_page(self, api_manager: ApiManager):
        """Проверка с невалидным номером страницы"""
        params = {"page": -1}

        response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        assert response.status_code == 400

    def test_get_movies_invalid_page_size(self, api_manager: ApiManager):
        """Проверка с невалидным размером страницы"""
        params = {"pageSize": 0}

        response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        assert response.status_code == 400

    def test_get_movies_min_price_greater_than_max(self, api_manager: ApiManager):
        """Проверка когда минимальная цена больше максимальной"""
        params = {"minPrice": 500, "maxPrice": 100}

        response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        assert response.status_code == 400