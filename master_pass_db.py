import sys
from Cryptodome.Random import get_random_bytes
import mysql.connector
from base64 import b64encode, b64decode


class MasterPassManager:
    def __init__(self):
        self.db = mysql.connector.connect(host='localhost', user='python', password='MYOP9317a', database='python',
                                          charset='utf8')
        self.cursor = self.db.cursor()

    def is_set(self):
        """
        Check if master password is set.
        :return:
        """
        query = 'SELECT setup FROM masterpass'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            query = 'INSERT INTO masterpass (salt, setup, test_str) VALUES (NULL, 0, NULL)'
            self.cursor.execute(query)
            self.db.commit()
            return False
        if result[0] == 0:
            return False
        else:
            return True

    def set_master_salt(self):
        """
        If master password is not set, generate salt for it.
        :return: False if master password is set, True when master password is not set.
        """
        if self.is_set():
            print('Master password already set', file=sys.stderr)
            return False
        salt = get_random_bytes(16)
        salt = b64encode(salt).decode('utf-8')
        query = "UPDATE masterpass SET salt = %s, setup = 1 WHERE salt IS NULL AND setup = 0 "
        self.cursor.execute(query, [salt])
        self.db.commit()
        return True

    def get_salt(self):
        """
        If master password is set, gets master password salt from database.
        :return: Bytes: master password salt or None if master password is not set.
        """
        if not self.is_set():
            print('Master password is not set', file=sys.stderr)
            return None
        query = 'SELECT salt FROM masterpass'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            print('Error fetching salt from db', file=sys.stderr)
            return ''
        return b64decode(result[0])

    def set_test_str(self, test_str: str, nonce: str, tag: str):
        query = 'UPDATE masterpass SET test_str = %s, nonce = %s, tag = %s'
        self.cursor.execute(query, [test_str, nonce, tag])
        self.db.commit()

    def get_test_str(self):
        query = 'SELECT test_str, salt, nonce, tag FROM masterpass'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return {'cipher_text': result[0], 'salt': result[1], 'nonce': result[2], 'tag': result[3]}
