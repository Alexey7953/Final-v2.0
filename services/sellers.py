import sqlite3
from src.exceptions import ServiceError


class SellersServiceError(ServiceError):
    service = "sellers"


class SellerDoesNotExistsError(object):
    pass


class SellerCreationError(object):
    pass


class SellerBadRequest(object):
    pass


class SellerUpdateError(object):
    pass


class SellerDeleteError(object):
    pass


class SellersService:
    """Сервис взаимодействия с таблицей seller"""
    def __init__(self, connection):
        self.connection = connection
        
    def get_id(self, user_id: int) -> int:
        """Получение id продавца"""
        cursor = self.connection.execute(
            """
            SELECT id
            FROM seller
            WHERE  account_id = ?
            """,
            (user_id,)
        )
        
        seller_id = cursor.fetchone()
        
        if not seller_id:
            raise SellerDoesNotExistsError
        return seller_id["id"]
    
    def read(self, seller_id: int = None, user_id: int = None) -> dict:
        """
         Чтение данных продавца из базы. Поиск по id продавца или пользователя.
        Возвращает результат в виде словаря
        """
        query = (
            """
            SELECT seller.phone, seller.zip_code, seller.street, seller.home, zipcode.city_id
            FROM seller
            """
        )
        if seller_id is not None:
            query += 'WHERE seller.id = ?'
            params = (seller_id,)
        elif user_id is not None:
            query += """
            JOIN account ON account.id = seller.account_id
            WHERE account.id = ?
            """
            params = (user_id,)
            
        else:
            raise SellerBadRequest
        cursor = self.connection.execute(query, params)
        seller = cursor.fetchone()
        
        if seller is None:
            raise SellerDoesNotExistsError
        return dict(seller)
    
    def create(self, seller_data: dict, user_id: int) -> int:
        """Запись новго продавца в базу. Возвращается id"""
        query = (
            """
            INSERT INTO seller (phone, zip_code, street, home, account_id) VALUES (?,?,?,?,?)
            """
        )
        
        params = (
            seller_data["phone"],
            seller_data["zip_code"],
            seller_data["street"],
            seller_data["home"],
            user_id,
        )
        
        try:
            cursor = self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise SellerCreationError
        else:
            return cursor.lastrowid
        
    def update(self, user_id: int, data: dict):
        """Частичное редактирование продавца"""
        seller_id = self.get_id(user_id)
        
        new_data = {
            "phone": data.get("phone"),
            "zip_code": data.get("zip_code"),
            "street": data.get("street"),
            "home": data.get("home"),
        }
        
        keys = ','.join(f'{key} = ?' for key in new_data if new_data[key] is not None)
        values = [value for value in new_data.values() if value is not None]
        query = f'UPDATE seller SET {keys} WHERE id = ?'
        params = (*values, seller_id)
        
        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise SellerUpdateError
        
    def delete(self, user_id: int):
        """Удаление продавца из базы"""
        try:
            seller_id = self.get_id(user_id)
            self.connection.execute('DELETE FROM seller WHERE id = ?', (seller_id,))
            self.connection.commit()
        except SellerDoesNotExistsError:
            raise SellerDeleteError
