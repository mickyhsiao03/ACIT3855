import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-kafka.eastus2.cloudapp.azure.com", user="root", 
password="2705895a", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
          DROP TABLE stock_number, date_range
          ''')

db_conn.commit()
db_conn.close()
