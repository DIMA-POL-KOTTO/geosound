import os
import psycopg2

#Установка соединения с БД
conn = psycopg2.connect(host="localhost", database=os.environ['POSTGRES_DB'], user=os.environ['USERNAME_DB'],
                        password=os.environ['PASSWORD_DB'])

cur = conn.cursor()

#Создание таблицы


#Вставка строки




#Сохранение операции
conn.commit()

#Закрытие соединения
cur.close()