import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-kafka.eastus2.cloudapp.azure.com", user="root", 
password="2705895a", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS stock_number
          (id INT NOT NULL AUTO_INCREMENT, 
           investor_ID VARCHAR(250) NOT NULL,
           price_Date VARCHAR(100) NOT NULL,
           stock_Name VARCHAR(50) NOT NULL,
           stock_Number VARCHAR(10) NOT NULL,
           stock_Price INT NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT stock_number_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS date_range
          (id INT NOT NULL AUTO_INCREMENT, 
           investor_ID VARCHAR(250) NOT NULL,
           day INT NOT NULL,
           month VARCHAR(15) NOT NULL,
           time VARCHAR(50) NOT NULL,
           year VARCHAR(5) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT date_range_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
