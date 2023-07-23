import psycopg2
import json

class DatabaseService:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def add_nodes(self, data):
        self.cur.execute("INSERT INTO nodes (data) VALUES (%s)", (json.dumps(data),))
        self.conn.commit()

    def get_nodes(self):
        self.cur.execute("SELECT data FROM nodes")
        test = self.cur.fetchall()
        return [record[0] for record in test]

    def add_edges(self, data):
        self.cur.execute("INSERT INTO edges (data) VALUES (%s)", (json.dumps(data),))
        self.conn.commit()

    def get_edges(self):
        self.cur.execute("SELECT data FROM edges")
        return [record[0] for record in self.cur.fetchall()]

    def add_thresholds(self, data):
        self.cur.execute("INSERT INTO thresholds (data) VALUES (%s)", (json.dumps(data),))
        self.conn.commit()

    def get_thresholds(self):
        self.cur.execute("SELECT data FROM thresholds")
        return [record[0] for record in self.cur.fetchall()]

    def add_logs(self, data):
        self.cur.execute("INSERT INTO logs (data) VALUES (%s)", (json.dumps(data),))
        self.conn.commit()

    def get_logs(self):
        self.cur.execute("SELECT data FROM logs")
        return [record[0] for record in self.cur.fetchall()]

    def get_url_data(self):
        self.cur.execute("SELECT data FROM url_data")
        return [record[0] for record in self.cur.fetchall()]