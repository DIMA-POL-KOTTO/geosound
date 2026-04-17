import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class FDataBase():
    def __init__(self):
        # Установка соединения с БД
        self.conn = psycopg2.connect(
            host="localhost",
            database=os.environ['POSTGRES_DB'],
            user=os.environ['USERNAME_DB'],
            password=os.environ['PASSWORD_DB']
        )
        self.cur = self.conn.cursor()
    def close(self):
        self.cur.close()
        self.conn.close()
    def get_tracks_with_audio(self):
        self.cur.execute('SELECT * FROM tracks WHERE audio_url IS NOT NULL;')
        return self.cur.fetchall()
    def get_user_by_id(self, user_id):
        self.cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        return self.cur.fetchone()
    def get_user_by_username(self, username):
        self.cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        return self.cur.fetchone()
    def get_id_by_username_or_email(self, username, email):
        self.cur.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        return self.cur.fetchone()
    def get_username_and_email_by_username_or_email(self, username, email):
        self.cur.execute('SELECT username, email FROM users WHERE username=%s OR email = %s', (username, email))
        return self.cur.fetchone()
    def add_user(self, username, email, password_hash):
        self.cur.execute('INSERT INTO users (username, email, password_hash)'
                                        'VALUES (%s, %s, %s)',
                                        (username, email, password_hash))
        self.conn.commit()
    def add_playlist(self, name, owner_id):
        self.cur.execute('INSERT INTO playlists (name, owner_id) VALUES(%s, %s)', (name, owner_id))
        self.conn.commit()
    def get_playlists_by_owner(self, owner_id):
        self.cur.execute('SELECT * FROM playlists WHERE owner_id = %s', (owner_id))
        return self.cur.fetchall()
    def add_track_to_playlist(self, playlist_id, track_id):
        self.cur.execute('INSERT INTO playlist_track(playlist_id, track_id) VALUES (%s, %s)', (playlist_id, track_id))
        self.conn.commit()
    def get_playlist_by_id(self, playlist_id):
        self.cur.execute('SELECT * FROM playlists WHERE id = %s', (playlist_id,))
        return self.cur.fetchone()
    def get_tracks_by_playlist(self, playlist_id):
        self.cur.execute('SELECT * FROM tracks t '
                         'JOIN playlist_track pt ON t.id = pt.track_id '
                         'WHERE pt.playlist_id = %s', (playlist_id, ))
        return self.cur.fetchall()
    def get_zones_by_owner(self, owner_id):
        self.cur.execute("SELECT * FROM zones WHERE owner_id = %s", (owner_id, ))
        return self.cur.fetchall()
    def add_zone_for_user(self, owner_id, name, polygon):
        self.cur.execute("INSERT INTO zones(owner_id, name, polygon) "
                         "VALUES (%s, %s, ST_GeomFromText(%s, 4326))", (owner_id, name, polygon))
        self.conn.commit()
        return self.cur.fetchone()[0]  # ← возвращаем ID
    def update_zone(self, zone_id, polygon):
        self.cur.execute("UPDATE zones SET polygon = ST_GeomFromText(%s, 4326) "
                         "WHERE id = %s", (polygon, zone_id))
        self.conn.commit()
