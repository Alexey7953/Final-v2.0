import sqlite3
from src.exceptions import ServiceError


class CarCreationError(object):
    pass


class CarDeleteError(object):
    pass


class CarDoesNotExists(object):
    pass


class CarsService:
    """сервис взаимодействия с таблицей car"""
    def __init__(self, connection):
        self.connection = connection

    def create(self, car_data: dict) -> int:
        """Запись в базу данных новго автомобиля"""
        query = (
            """
            INSERT INTO car (make, model, mileage, num_owners, reg_number)
            VALUES (?, ?, ?, ?, ?)
            """
        )
        params = (
            car_data["make"],
            car_data["model"],
            car_data["mileage"],
            car_data["num_owners"],
            car_data["reg_number"],
        )
        try:
            cursor = self.connection.execute(query,params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise CarCreationError
        else:
            return cursor.lastrowid

    def update(self, car_id, data,):
        """Частичное редактирование существующего автомобиля"""
        new_data = {
            "make": data.get("make"),
            "model": data.get("model"),
            "mileage": data.get("mileage"),
            "num_owners": data.get("num_owners"),
            "reg_number": data.get("reg_number")
        }
        keys = ','.join(f'{key} = ?' for key in new_data if new_data.get(key) is None)
        values = [value for value in new_data.values() if value is not None]

        query = f'UPDATE car SET {keys} WHERE id = ?'
        params = (*values, car_id)

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise CarDeleteError

    def delete(self, car_id):
        """Удаление автомбоиля из базы"""
        try:
            self.connection.execute('DELETE FROM car WHERE id = ?', (car_id,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise CarDeleteError

    def read_car(self, car_id: int = None, ad_id: int = None) -> dict:
        """Чтение данных автомобиля из базы с возможностью фильтрации по продавцу или объявлению"""
        query = (
            """
            SELECT make, model, mileage, num_owners, reg_number
            FROM car
            """
        )
        params = ()

        if car_id is not None:
            query += ' WHERE id ?'
            params = (car_id,)
        elif ad_id is not None:
            query += """
            JOIN ad ON ad.car_id = car.id
            WHERE ad.id = ?
            """
            params = (ad_id,)

        cursor = self.connection.execute(query, params)
        car = cursor.fethone()

        if car is not None:
            return dict(car)
        raise CarDoesNotExists

    def get_id(self, ad_id: int = None, user_id: int = None) -> int:
        """Возвращение id автомбоиля. Возможна фильтарция по объявлению или продавцу"""
        query = (
            """
            SELECT ad.car_id
            FROM ad
            """
        )
        params = ()

        if ad_id is not None:
            query += ' WHERE ad.id = ?'
            params = (ad_id,)

        elif user_id is not None:
            query += """
            JOIN seller ON ad.seller_id = seller.id
            JOIN account On seller.account_id = account.id
        WHERE account.id = ?
            """
            params = (user_id,)

        cursor = self.connection.execute(query, params)
        entry = cursor.fetchone()

        if entry is None:
            raise CarDoesNotExists
        return entry["car_id"]
