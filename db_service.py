import json

import psycopg2


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

    def add_threshold(self, data):
        self.cur.execute("SELECT * FROM threshold")
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO threshold (data) VALUES (%s)", (json.dumps(data),))
        else:
            self.cur.execute("UPDATE threshold SET data = %s", (json.dumps(data),))
        self.conn.commit()

    def get_threshold(self):
        self.cur.execute("SELECT data FROM threshold LIMIT 1")
        result = self.cur.fetchone()
        return result[0] if result else None

    def add_recommendations(self, data, node_name):
        self.cur.execute("SELECT * FROM recommendations WHERE node_name = %s", (node_name,))
        if self.cur.fetchone() is None:
            self.cur.execute("""
                INSERT INTO recommendations (data, node_name) 
                VALUES (%s, %s)""",
                             (data, node_name))
        else:
            self.cur.execute("""
                UPDATE recommendations 
                SET data = %s
                WHERE node_name = %s""",
                             (data, node_name))
        self.conn.commit()

    def get_recommendations(self, node_name):
        self.cur.execute("SELECT data FROM recommendations WHERE node_name = %s", (node_name,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def add_logs(self, data):
        self.cur.execute("INSERT INTO logs (data) VALUES (%s)", (json.dumps(data),))
        self.conn.commit()

    def get_logs(self):
        self.cur.execute("SELECT data FROM logs")
        return [record[0] for record in self.cur.fetchall()]

    def get_url_data(self):
        self.cur.execute("SELECT data FROM url_data")
        return [record[0] for record in self.cur.fetchall()]
