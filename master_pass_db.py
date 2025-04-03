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
        query = 'SELECT setup FROM masterpass'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            query = 'INSERT INTO masterpass (salt, setup) VALUES (NULL, 0)'
            self.cursor.execute(query)
            self.db.commit()
            return False
        if result[0] == 0:
            return False
        else:
            return True

    def set_master_salt(self):
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
        if not self.is_set():
            print('Master password is not set', file=sys.stderr)
            return ''
        query = 'SELECT salt FROM masterpass'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            print('Error fetching salt from db', file=sys.stderr)
            return ''
        return b64decode(result[0])
