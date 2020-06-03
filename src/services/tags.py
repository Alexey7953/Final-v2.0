import sqlite3
from src.exceptions import ServiceError


class TagsServiceError(ServiceError):
    service = 'tags'


class TagDoesNotExistsError(object):
    pass


class TagsCreationError(object):
    pass


class TagAdRelationCreationError(object):
    pass


class TagsService:
    def __init__(self, connection):
        self.connection = connection

    """Сервис взаимодействия с таблице tag"""

    def add_to_ad(self, tag: str, ad_id: int):
        """Добавление тэга к объявлению. Создание тэга при его отсутствии"""
        try:
            tag_id = self.get_tag_id(tag)
        except TagDoesNotExistsError:
            tag_id = self.create_tag(tag)

        self.add_relation(tag_id=tag_id, ad_id=ad_id)

    def create_tag(self, tag: str) -> int:
        """Запись новго тега в базу данных"""
        try:
            cursor = self.connection.execute('INSERT INTO tag (name) VALUES (?)', (tag,))
            self.connection.commit()

        except sqlite3.IntegrityError:
            raise TagsCreationError
        else:
            return cursor.lastrowid

    def get_tag_id(self, name: str) -> int:
        """Получение id тега по имени"""
        cursor = self.connection.execute('SELECT id FROM tag WHERE name = ?', (name,))
        tag = cursor.fetchone()
        if tag is None:
            raise TagDoesNotExistsError
        return tag["id"]

    def add_relation(self, tag_id: int, ad_id: int):
        """Сощдание MANY to MANY связи тэга и объявления"""
        cursor = self.connection.execute('SELECT ad_id FROM ad_tag WHERE tag_id = ?', (tag_id,))
        adtag_relation = cursor.fetchone()

        if adtag_relation is not None and adtag_relation["ad_id"] == ad_id:
            return

        try:
            self.connection.execute('INSERT INTO ad_tag (tag_id, ad_id) VALUES (?, ?)', (tag_id, ad_id))
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise TagAdRelationCreationError

    def read_tag(self, ad_id: int) -> list:
        """Получение списка тэгов из базы данных по id объявления"""
        query = (
            """
            SELECT tag.name
            FROM tag
                JOIN ad_tag ON tag.id = ad_tag.tag_id
            WHERE ad_tag.ad_id = ?
            """
        )
        params = (ad_id,)
        cursor = self.connection.execute(query, params)

        return [entry["name"] for entry in cursor.fetchall()]
