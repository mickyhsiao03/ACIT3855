import sqlite3 
 
conn = sqlite3.connect('data.sqlite') 
 
c = conn.cursor() 
c.execute(''' 
          CREATE TABLE stats 
          (id INTEGER PRIMARY KEY ASC,  
           num_stock INTEGER, 
           num_dRange INTEGER, 
           top_stock_price INTEGER NOT NULL, 
           top_stock_number VARCHAR(50) NOT NULL, 
           top_stock_name VARCHAR(50) NOT NULL, 
           last_updated VARCHAR(100) NOT NULL) 
          ''') 
 
conn.commit() 
conn.close()