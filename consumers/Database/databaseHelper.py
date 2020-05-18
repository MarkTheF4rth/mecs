import sqlite3
from sqlite3 import Error

class DBConnection:
    connection = None

    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def execute_statement(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Error as e:
            print(e)

    def execute_query(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
        except Error as e:
            print(e)
        return cursor.fetchall()