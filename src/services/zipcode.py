import sqlite3

from src.exceptions import ServiceError


class ZipcodesServiceError(ServiceError):
    service = 'zipcode'


class Zip_codesCreationError(ZipcodesServiceError):
    pass


class Zip_codesUpdateError(ZipcodesServiceError):
    pass


class ZipcodesCreationError(ZipcodesServiceError):
    pass


class ZipcodesService:
    """Сервис взаимодействия с таблицей zipcode"""
    def __init__(self, connection):
        self.connection = connection

    def _check_existence(self, zip_code: str) -> bool:
        """Проверка существования индекса в базе"""
        query = (
            """
            SELECT *
            FROM zipcode
            WHERE zip_code = ?
            """
        )
        params = (zip_code,)

        cursor = self.connection.execute(query, params)
        if cursor.fetchone() is not None:
            return True
        return False

    def create(self, zip_code_data: dict):
        """Создание новой связи в базе"""
        zip_code = zip_code_data["zip_code"]
        city_id = zip_code_data["city_id"]

        query = (
            """
            INSERT INTO zipcode (zip_code, city_id) VALUES (?, ?)
            """
        )

        params = (
            zip_code,
            city_id,
        )

        if self._check_existence(zip_code):
            return

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ZipcodesCreationError

    def update(self, data: dict):
        """Частичное редактирование записи в базе"""
        zip_code = data.get("zip_code")
        city_id = data.get("city_id")

        if not all((zip_code, city_id)):
            return

        if self._check_existence(zip_code):
            self.connection.execute(
                'UPDATE zipcode SET city_id = ? WHERE zip_code = ?',
                (city_id, zip_code)
            )

        else:
            self.create(
                {
                    "zip_code": zip_code,
                    "city_id": city_id,
                }
            )
