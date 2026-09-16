import sqlite3 
conn = sqlite3.connect("warehouse.db") 
c = conn.cursor() 
c.execute("CREATE TABLE IF NOT EXISTS promo_uses (id INTEGER PRIMARY KEY, code TEXT, customer_id INTEGER)") 
c.execute("CREATE TABLE IF NOT EXISTS deliveries (id INTEGER PRIMARY KEY, order_id INTEGER, slot TEXT)") 
conn.commit() 
conn.close() 
print("setup_modules OK") 
