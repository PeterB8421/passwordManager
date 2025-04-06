import mysql.connector
import file_enc


class DbManager:
    def __init__(self):
        self.db = mysql.connector.connect(host='localhost', user='python', password='MYOP9317a', database='python', charset='utf8')
        self.cursor = self.db.cursor()

    def insert(self, username, password, url, salt, nonce, tag, key, note=""):
        """
        Inserts a password into the database.
        :param username: Username for given service
        :param password: Password for given service, needs to be encrypted before insertion.
        :param url: Service URL.
        :param salt: Password salt.
        :param nonce: Password nonce.
        :param tag: Password tag.
        :param key: Key for encrypting salt file.
        :param note: Note for given password.
        :return:
        """
        query = "INSERT INTO passmanager (username, password, url, note) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (username, password, url, note))
        self.db.commit()
        id = self.cursor.lastrowid
        salts = file_enc.read_from_csv('data/salts.csv', key)
        new_row = {'id': id, 'salt': salt, 'nonce': nonce, 'tag': tag}
        salts.append(new_row)
        file_enc.write_to_csv(salts, 'data/salts.csv', ['id', 'salt', 'nonce', 'tag'], key)

    def get_by_url(self, url):
        """
        Gets a set of passwords from the database using the given url.
        :param url: URL to search for.
        :return: Array of rows or None if nothing was found.
        """
        query = "SELECT id, url, username, note FROM passmanager WHERE url LIKE %s"
        self.cursor.execute(query, ['%' + url + '%'])
        rows = self.cursor.fetchall()
        return rows

    def get_by_id(self, row_id):
        """
        Gets a row from the database using the given id.
        :param row_id: Row ID
        :return: Tuple of row that was found or None if nothing was found.
        """
        query = "SELECT * FROM passmanager WHERE id = %s"
        self.cursor.execute(query, [row_id])
        return self.cursor.fetchone()
