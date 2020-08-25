import sqlite3
import hashlib


class Accounts:
    conn = None

    def __init__(self, db_name: str, encoding: str):
        self.db_name = db_name
        self.encoding = encoding
        self.conn = sqlite3.connect(database=self.db_name, check_same_thread=False, isolation_level='EXCLUSIVE')

    def create_tables(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "create table if not exists User (id integer PRIMARY KEY, nick text, password blob);"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            self.log_err('Unable to create tables')
        cursor.close()
        # TODO table for messages

    def add_user(self, nick: str, password: str):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select id from User where nick = ?;", (nick,))
            if len(cursor.fetchall()) == 0:
                raise Exception("nick already taken")

            new_user = {"nick": nick, "password": hashlib.md5(bytes(password, self.encoding)).digest()}
            cursor.execute("insert into User (nick, password) values (:nick, :password)", new_user)
            self.conn.commit()
        except sqlite3.OperationalError:
            self.log_err(f"unable to add user_name: {nick}")
        cursor.close()

    def delete_user(self, idx: int):
        cursor = self.conn.cursor()
        try:
            cursor.execute("delete from User where id = ?;", (idx,))
            self.conn.commit()
        except sqlite3.OperationalError:
            self.log_err(f"unable to delete user_id: {id}")
        cursor.close()

    def is_valid(self, pswd: str, original_pswd: str) -> bool:
        print(hashlib.md5(bytes(pswd, self.encoding)).digest(), ' =?= ', original_pswd)
        return hashlib.md5(bytes(pswd, self.encoding)).digest() == original_pswd

    def get_id(self, nick: str, password: str):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select id, password from User where nick = ?;", (nick,))
            user_id, user_pwd = cursor.fetchone()
            print(user_id, user_pwd)
            if self.is_valid(password, user_pwd):
                return user_id
        except sqlite3.OperationalError:
            self.log_err(f"unable to get id of user_name: {nick}")
        finally:
            cursor.close()
        return None

    def close(self):
        self.conn.close()

    @staticmethod
    def log_err(self, msg):
        print(f'\033[1;31m{msg}\033[0m')
