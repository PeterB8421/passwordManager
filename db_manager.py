import sys

import mysql.connector


def get_config(filename='config.cfg'):
    required_keys = {"host", "user", "password", "database"}
    cfg = {}

    with open(filename, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            if ":" not in line:
                continue

            key, value = [part.strip() for part in line.split(":", 1)]
            if key in required_keys:
                # save only expected keys
                cfg[key] = value

    missing = required_keys - cfg.keys()
    if missing:
        raise ValueError(f"Missing config item(s): {', '.join(missing)}")

    return cfg


class DbManager:
    def __init__(self):
        try:
            cfg = get_config()
        except ValueError as e:
            print(f'Config file incomplete! {e}', file=sys.stderr)
            exit(1)
        self.db = mysql.connector.connect(host=cfg['host'], user=cfg['user'], password=cfg['password'],
                                          database=cfg['database'], charset='utf8')
        self.cursor = self.db.cursor()

    def insert(self, username, password, url, salt, nonce, tag, note=""):
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
        query = "INSERT INTO passmanager (username, password, url, note, salt, nonce, tag) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, (username, password, url, note, salt, nonce, tag))
        self.db.commit()

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
        """
        Returns all rows from the database.
        :return: List of tuples with row data
        """
        query = "SELECT * FROM passmanager"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_by_id(self, row_id, username, password, url, note, salt, nonce, tag):
        """
        Updates a row in the database using the given id.
        :param row_id: ID of row to update.
        :param username: Username for given service.
        :param password: Password for given service.
        :param url: URl or domain for given service.
        :param note: User's note to set for that row
        :param salt: Salt for this password
        :param nonce: Nonce for AES algorithm
        :param tag: MAC for AES algorithm
        :return: True if update was successful.
        """
        query = "UPDATE passmanager SET url = %s, note = %s, username = %s, password = %s, salt = %s, nonce = %s, tag = %s WHERE id = %s"
        self.cursor.execute(query, [url, note, username, password, salt, nonce, tag, row_id])
        self.db.commit()
        return True

    def delete_by_id(self, row_id):
        """
        Deletes a row from the database using the given id.
        :param row_id: ID of row to delete.
        :return:
        """
        query = "DELETE FROM passmanager WHERE id = %s"
        self.cursor.execute(query, [row_id])
        self.db.commit()
