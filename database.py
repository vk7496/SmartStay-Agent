import sqlite3

def init_db():
    conn = sqlite3.connect('data/hostel_db.sqlite')
    c = conn.cursor()
    # جدول اتاق‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS rooms 
                 (id INTEGER PRIMARY KEY, branch TEXT, capacity INTEGER)''')
    # جدول رزروها
    c.execute('''CREATE TABLE IF NOT EXISTS reservations 
                 (id INTEGER PRIMARY KEY, branch TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def get_rooms():
    conn = sqlite3.connect('data/hostel_db.sqlite')
    # کد خواندن از دیتابیس
    conn.close()
    return data
