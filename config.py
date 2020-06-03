import os


class Config:
    DB_CONNECTION = os.getenv('DB_CONNECTION', 'example.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'secrets').encode()
