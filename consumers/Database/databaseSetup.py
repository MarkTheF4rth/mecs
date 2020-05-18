import os
from databaseHelper import DBConnection

class DatabaseSetup:
    def __init__(self, db_loc):
        self.connection = DBConnection(db_loc)


    def purge(self):
        drop_events = 'DROP TABLE IF EXISTS events;'

        self.connection.execute_statement(drop_events)


    def setup(self):
        create_events = """CREATE TABLE IF NOT EXISTS events (
            id integer PRIMARY KEY,
            time real,
            node text,
            event integer,
            level text);"""
        
        self.connection.execute_statement(create_events)


if __name__ == "__main__":
    db_loc = os.environ['SQLITE_DB_LOC']
    # set up a database if one doesn't exist
    dbsetup = DatabaseSetup(db_loc)
    print('removing old database')
    dbsetup.purge()
    print('creating new database')
    dbsetup.setup()
