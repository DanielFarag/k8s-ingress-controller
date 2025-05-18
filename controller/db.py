import sqlite3

class DB:
    def __init__(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    path TEXT NOT NULL
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
    
    def all(self):
        try:
            self.cursor.execute("SELECT * FROM entries")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return []

    def insert(self, data):

        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())

            sql = f"INSERT INTO entries ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def delete(self, id):
        try:
            sql = f"DELETE FROM entries WHERE id=?"
            self.cursor.execute(sql, (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def update(self, data):
        try:
            data = dict(data)
            id = data.get("id")
            data.pop("id", None)

            assignments = ', '.join([f"{key}=?" for key in data])
            values = tuple(data.values()) + (id,)
            sql = f"UPDATE entries SET {assignments} WHERE id=?"
            self.cursor.execute(sql, values)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")


    def close(self):
        self.conn.close()
