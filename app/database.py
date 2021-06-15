from app import config
from google.cloud.sql.connector import connector
import hashlib
from uuid import uuid1

class SQLConnection():
    def __init__(self):
        self.pri = config['DBPRI']
        self.driver = config['DBDRIVER']
        self.user = config['DBUSER']
        self.password = config['DBPASSWORD']
        self.db = config['DBNAME']

    def execute_sql(self, func, *args):
        conn = connector.connect(self.pri, self.driver, user=self.user, password=self.password, db=self.db)
        self.cur = conn.cursor()
        self.create_tables()
        result = func(*args)
        conn.commit()
        self.cur.close()
        conn.close()
        return result

    def drop_tables(self):
        self.cur.execute(
            """
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS documents;
            """
        )

    def create_tables(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id uuid NOT NULL UNIQUE,
                firstname varchar,
                lastname varchar,
                link1 varchar,
                link2 varchar,
                email varchar,
                password text,
                type boolean
            );
            CREATE TABLE IF NOT EXISTS documents (
                document_id uuid NOT NULL UNIQUE,
                editor uuid,
                document_type varchar NOT NULL,
                title varchar NOT NULL UNIQUE,
                summary text NOT NULL,
                full_description text NOT NULL,
                relevant_links text[5]
            );
            """
        )

    def create_user(self, user_id=None):
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

    # def is_admin_user(self, user_id):
    #     self.cur.execute(
    #         """
    #         SELECT email, type
    #         FROM users
    #         WHERE user_id = '{0}';
    #         """.format(user_id)
    #     )
    #     email_type = self.cur.fetchone()

    #     if email_type == None:
    #         return None
    #     if int(email_type[1]) == 1:
    #         return email_type[0]
    #     return None

    def get_user(self, user_id):
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

    def edit_profile(self, user_id, firstname, lastname, link1='', link2=''):
        self.cur.execute(
            """
            UPDATE users
            SET firstname = '{0}', lastname = '{1}', link1 = '{2}', link2 = '{3}'
            WHERE user_id = '{4}';
            """.format(firstname, lastname, link1, link2, user_id)
        )
        return firstname, lastname

    def get_profile(self, user_id):
        self.cur.execute(
            """
            SELECT firstname, lastname, link1, link2, email
            FROM users
            WHERE user_id = '{0}';
            """.format(user_id)
        )
        profile = self.cur.fetchone()
        firstname = str(profile[0] or '')
        lastname = str(profile[1] or '')
        link1 = str(profile[2] or '')
        link2 = str(profile[3] or '')

        return [profile[4], firstname, lastname, link1, link2]

    def create_document(self, user_id, document_type, title, summary, full_description, link1, link2, link3, link4, link5):
        document_id = str(uuid1())
        self.cur.execute(
            """
            INSERT INTO documents (document_id, editor, document_type, title, summary, full_description, relevant_links)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{{"{6}", "{7}", "{8}", "{9}", "{10}"}}')
            """.format(document_id, user_id, document_type, title, summary, full_description, link1, link2, link3, link4, link5)
        )
        return document_id

    def get_document(self, document_id):
        self.cur.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = '{0}';
            """.format(document_id)
        )
        document = self.cur.fetchone()
        if document == None:
            return None

        editor = self.get_user(document[1])

        return {
            'id': document[0],
            'document_type': document[2],
            'editor_name': (editor[1] + ' ' + editor[2]),
            'title': document[3],
            'summary': document[4],
            'full_description': document[5],
            'links': document[6]
        }

    def get_all_documents(self):
        self.cur.execute(
            """
            SELECT document_id
            FROM documents
            """
        )
        documents_id = self.cur.fetchall()
        documents = []
        if documents_id != None and len(documents_id) > 0:
            for document_id in documents_id[0]:
                documents.append(self.get_document(document_id))
        return documents