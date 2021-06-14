from app import config
from google.cloud.sql.connector import connector

def SQLConnection():
    def __init__(self):
        self.conn = connector.connect(
            config['DBPRI'],
            config['DBDRIVER'],
            config['DBUSER'],
            config['DBPASSWORD'],
            config['DBNAME']
        )
        self.cur = self.conn.cursor()