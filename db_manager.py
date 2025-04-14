import mysql.connector
import file_enc


def get_salt_by_id(record_id, key):
    salts = file_enc.read_from_csv('data/salts.csv', key)
    salt_dict = None
    for record in salts:
        if record['id'] == str(record_id):
            salt_dict = record
            break
    return salt_dict, salts


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

    def get_all(self):
        query = "SELECT * FROM passmanager"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_by_id(self, key, row_id, username, password, url, note, salt, nonce, tag):
        salt_dict, salts = get_salt_by_id(row_id, key)
        if salt_dict is None:
            return False
        print('Before: ', salts)
        salts.remove(salt_dict)
        salt_dict['salt'] = salt
        salt_dict['nonce'] = nonce
        salt_dict['tag'] = tag
        salts.append(salt_dict)
        print('After: ', salts)
        file_enc.write_to_csv(salts, 'data/salts.csv', ['id', 'salt', 'nonce', 'tag'], key)

        query = "UPDATE passmanager SET url = %s, note = %s, username = %s, password = %s WHERE id = %s"
        self.cursor.execute(query, [url, note, username, password, row_id])
        self.db.commit()
        return True

    def delete_by_id(self, row_id, key):
        query = "DELETE FROM passmanager WHERE id = %s"
        self.cursor.execute(query, [row_id])
        self.db.commit()

        salt_dict, salts = get_salt_by_id(row_id, key)
        if salt_dict is not None:
            salts.remove(salt_dict)
            file_enc.write_to_csv(salts, 'data/salts.csv', ['id', 'salt', 'nonce', 'tag'], key)
