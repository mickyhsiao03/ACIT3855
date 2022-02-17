import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root", 
password="2705895a", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
          DROP TABLE stock_number, date_range
          ''')

db_conn.commit()
db_conn.close()
