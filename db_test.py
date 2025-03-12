import mysql.connector


class DbManager:
    def __init__(self):
        self.db = mysql.connector.connect(host='localhost', user='python', password='MYOP9317a', database='python', charset='utf8')
        self.cursor = self.db.cursor()

    def insert(self, username, password, url, salt, nonce, tag, note=""):
        query = "INSERT INTO passmanager (username, password, url, note, salt, nonce, tag) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, (username, password, url, note, salt, nonce, tag))
        self.db.commit()

    def get_by_url(self, url):
        query = "SELECT id, url, username, note FROM passmanager WHERE url LIKE %s"
        self.cursor.execute(query, ['%' + url + '%'])
        rows = self.cursor.fetchall()
        return rows

    def get_by_id(self, id):
        query = "SELECT * FROM passmanager WHERE id = %s"
        self.cursor.execute(query, [id])
        return self.cursor.fetchone()
