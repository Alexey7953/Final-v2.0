import sqlite3
from blueprints import image
from src.exceptions import ServiceError


class ImageServiceError(object):
    pass


class ImageUpdateError(object):
    pass


class ImageService:
    def __init__(self, connection):
        self.connection = connection

    def create_image(self, url):
        """ Запись изображения в базу данных """
        query = (
            """
            INSERT INTO image (url, car_id) VALUES (?, 0)
            """
        )
        params = (url,)
        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ImageServiceError

    def update_image(self, image_data: dict, car_id: int):
        """Частичное редактирование данных изображения"""
        query = (
            """
            UPDATE image SET title = ?, car_id = ? WHERE url = ?
            """
        )

        params = (image_data["title"], car_id, image_data["url"])

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ImageUpdateError

    def read_image(self, car_id: int = None, ad_id: int= None) -> list:
        """Чтение об изображениях из базы"""
        query = (
            """
            SELECT image.title, image.url
            FROM image
            """
        )
        params = ()

        if car_id is not None:
            query += """WHERE car_id = ?"""
            params = (car_id,)

        elif ad_id is not None:
            query += """
                JOIN ad on image.car_id = ad.car_id
            WHERE ad.id = ?
            """
            params = (ad_id,)

        cursor = self.connection.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

