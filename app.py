import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    #Установка соединения с БД
    conn = psycopg2.connect(host="localhost", database=os.environ['POSTGRES_DB'], user=os.environ['USERNAME_DB'],
                            password=os.environ['PASSWORD_DB'])
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tracks;')
    tracks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tracks=tracks)