import mysql.connector
import file_enc


class DbManager:
    def __init__(self):
        self.db = mysql.connector.connect(host='localhost', user='python', password='MYOP9317a', database='python', charset='utf8')
        self.cursor = self.db.cursor()

    def insert(self, username, password, url, salt, nonce, tag, note=""):
        query = "INSERT INTO passmanager (username, password, url, note) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (username, password, url, note))
        self.db.commit()
        id = self.cursor.lastrowid
        salts = file_enc.read_from_csv('data/salts.csv')
        new_row = {'id': id, 'salt': salt, 'nonce': nonce, 'tag': tag}
        salts.append(new_row)
        file_enc.write_to_csv(salts, 'data/salts.csv', ['id', 'salt', 'nonce', 'tag'])

    def get_by_url(self, url):
        query = "SELECT id, url, username, note FROM passmanager WHERE url LIKE %s"
        self.cursor.execute(query, ['%' + url + '%'])
        rows = self.cursor.fetchall()
        return rows

    def get_by_id(self, id):
        query = "SELECT * FROM passmanager WHERE id = %s"
        self.cursor.execute(query, [id])
        return self.cursor.fetchone()
