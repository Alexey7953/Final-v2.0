import sqlite3


from src.exceptions import ServiceError


class ColorServiceError(ServiceError):
    service = 'color'


class ColorCreationError(ServiceError):
    pass


class ColorDoesNotExists(ServiceError):
    pass


class CarColorRelationCreationError(ServiceError):
    pass


class ColorService:
    def __init__(self, connection):
        self.connection = connection

    def read_all_color(self, ad_id=None) -> list:
        """Получение списка всех цветов из базы. Возможна фильтрация по объявлению"""
        query = (
            """
            SELECT color.id, color.name, color.hex
            FROM color
            """
        )
        params = ()

        if ad_id is not None:
            query += """
                JOIN carcolor ON color.id = carcolor.color_id
                JOIN car ON carcolor.car_id = car.id
                JOIN ad ON car.id = ad.car_id
            WHERE ad.id = ?
            """
            params = (ad_id,)

        cursor = self.connection.execute(query, params)
        return [dict(entry) for entry in cursor.fetchall()]

    def create_color(self, name: str, hex: str) -> str:
        """Запись нового цвета в базу данных"""
        query = (
            """
            INSERT INTO color (name, hex) VALUES (?, ?)
            """
        )

        params = (name, hex)

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ColorCreationError

        return name

    def read_color(self, name: str) -> dict:
        """Получение списка всех цветов из базы."""
        query = (
            """
            SELECT *
            FROM color
            WHERE name = ?
            """
        )

        params = (name,)

        cursor = self.connection.execute(query, params)
        color = cursor.fetchone()

        if color is None:
            raise ColorDoesNotExists
        return dict(color)

    def add_to_car_color(self, color_id: int, car_id: int):
        """Создание MANY TO MANY связи цвета с машиной"""
        query = (
            """
            INSERT INTO carcolor (color_id, car_id) VALUES (?, ?)
            """
        )
        params = (color_id, car_id)

        cursor = self.connection.execute('SELECT name FROM color WHERE id = ?', (color_id,))
        color_name = cursor.fetchone()
        if color_name is None:
            return

        cursor = self.connection.execute('SELECT car_id FROM carcolor WHERE color_id = ?', (color_id,))
        carcolor_relation = cursor.fetchone()

        if carcolor_relation is not None and carcolor_relation["car_id"] == car_id:
            return

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise CarColorRelationCreationError
