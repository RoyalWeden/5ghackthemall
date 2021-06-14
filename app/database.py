from app import config
from google.cloud.sql.connector import connector
import hashlib
from uuid import uuid1

class SQLConnection():
    def __init__(self):
        self.conn = connector.connect(
            config['DBPRI'],
            config['DBDRIVER'],
            user=config['DBUSER'],
            password=config['DBPASSWORD'],
            db=config['DBNAME']
        )
        self.cur = self.conn.cursor()

    def drop_tables(self):
        self.cur.execute(
            """
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS use_cases;
            """
        )

    def create_tables(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id uuid NOT NULL UNIQUE,
                firstname varchar,
                lastname varchar,
                link1name varchar,
                link1 varchar,
                link2name varchar,
                link2 varchar,
                email varchar,
                password text,
                type boolean
            );
            CREATE TABLE IF NOT EXISTS document (
                use_case_id uuid NOT NULL UNIQUE,
                document_type boolean NOT NULL,
                title varchar NOT NULL UNIQUE,
                summary text NOT NULL,
                full_description text NOT NULL,
                relevant_links text[],
                editors uuid[]
            );
            """
        )

    def create_user(self, user_id=None):
        self.create_tables()
        if user_id == None:
            user_id = str(uuid1())
        self.cur.execute(
            """
            INSERT INTO users (user_id, type)
            VALUES ('{0}', false)
            ON CONFLICT DO NOTHING;
            """.format(user_id)
        )
        return user_id

    def set_admin_user(self, user_id, email, password):
        self.create_tables()
        dk = hashlib.pbkdf2_hmac('sha256', bytes(password.encode()), b'salt', 100000, dklen=512)
        self.cur.execute(
            """
            UPDATE users
            SET email = '{0}', password = '{1}', type = true
            WHERE user_id = '{2}';
            """.format(email, dk.hex(), user_id)
        )
        return email

    def is_admin_user(self, email, password):
        self.create_tables()
        self.cur.execute(
            """
            SELECT password, type, user_id
            FROM users
            WHERE email = '{0}';
            """.format(email)
        )
        pass_type = self.cur.fetchone()
        dk = hashlib.pbkdf2_hmac('sha256', bytes(password.encode()), b'salt', 100000, dklen=512)

        if pass_type == None:
            return None
        elif pass_type[0] == dk.hex() and int(pass_type[1]) == 1:
            return pass_type[2]
        return None

    def get_user(self, user_id):
        self.create_tables()
        self.cur.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = '{0}';
            """.format(user_id)
        )
        user = self.cur.fetchone()

        if user == None:
            return None
        else:
            return user