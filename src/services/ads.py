import sqlite3

from src.exceptions import ServiceError


class AdsError(ServiceError):
    service = 'ads'


class AdsCreationError(object):
    pass


class AdsUpdateError(object):
    pass


class AdsDeleteError(object):
    pass


class AdDoesNotExists(object):
    pass


class AdsService:
    """ Сервис взаимодействия с таблицей ad"""

    def __init__(self, connection):
        self.connection = connection

    def create_ad(self, seller_id: int, car_id: int, title: str, date: str) -> int:
        """Запись в базу нового объявления"""
        query = 'INSERT INTO ad (title, date, seller_id, car_id) VALUES (?, ?, ?, ?)'
        params = (title, date, seller_id, car_id)

        try:
            cursor = self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise AdsCreationError
        else:
            return cursor.lastrowid

    def update_ad(self, titile: str, ad_id: int):
        """Частичное редактирование существующего объявления"""
        query = 'UPDATE ad SET title = ? WHERE id = ?'
        params = (titile, ad_id)

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise AdsUpdateError

    def delete_ad(self, ad_id):
        """Удаление объявления из базы"""
        try:
            self.connection.execute('DELETE FROM ad WHERE id = ?', (ad_id,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise AdsDeleteError

    def read_ad(self, ad_id: int) -> dict:
        """Чтение объявления из базы"""
        query = (
            """
            SELECT ad.id, ad.seller_id, ad.title, ad.date
            FROM ad
            WHERE ad.id = ?
            """
        )

        params = (ad_id,)

        cursor = self.connection.execute(query, params)
        ads = cursor.fetchone()

        if ads is None:
            raise AdDoesNotExists
        return dict(ads)

    def generation_id(self, seller_id=None):
        """Возвращает генератор id всех объявлений, либо принадлежащие указанному продавцу"""
        query = (
            """
            SELECT ad.id
            FROM ad
            """
        )
        params = ()

        if seller_id is not None:
            query += """
                JOIN seller ON ad.seller_id = seller.id
                WHERE seller.id = ?
            """
            params = (seller_id)

            cursor = self.connection.execute(query, params)
            return (ad["id"] for ad in cursor.fetchall())
