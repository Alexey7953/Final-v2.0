import sqlite3

from src.exceptions import ServiceError


class CityServiceError(ServiceError):
    service = 'cities'


class CityDoesNotExists(CityServiceError):
    pass


class CityCreationError(CityServiceError):
    pass


class CitiesService:
    def __init__(self, connection):
        self.connection = connection

    def read_all(self):
        """ Получение списка всех городов из базы данных """
        query = (
            """
            SELECT *
            FROM city
            """
        )
        cursor = self.connection.execute(query)
        return [dict(entry) for entry in cursor.fetchall()]

    def create(self, name):
        """ Запись нового города в базу данных """

        query = (
            """
            INSERT INTO city (name) VALUES (?)
            """
        )

        params = (name,)

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise CityCreationError

        return name

    def read(self, name):
        """ Получение города из базы данных """
        query = (
            """
            SELECT *
            FROM city
            WHERE name = ?
            """
        )

        params = (name,)

        cursor = self.connection.execute(query, params)
        city = cursor.fetchone()

        if city is None:
            raise CityDoesNotExists
        return dict(city)
