import sqlite3
import os

DB_PATH = 'data/hostel_db.sqlite'

def init_db():
    """ایجاد پوشه data و جداول دیتابیس در صورت عدم وجود"""
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            location    TEXT NOT NULL,
            nights      INTEGER NOT NULL,
            checkin     TEXT,
            room_type   TEXT,
            notes       TEXT,
            status      TEXT NOT NULL DEFAULT "در انتظار تایید",
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    ''')

    # اگه دیتابیس قدیمی دارن، ستون‌های جدید رو اضافه می‌کنه بدون خطا
    for col, definition in [
        ("checkin",   "TEXT"),
        ("room_type", "TEXT"),
        ("notes",     "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE reservations ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # ستون قبلاً وجود داره

    conn.commit()
    conn.close()


def add_reservation(name, phone, location, nights, checkin=None, room_type=None, notes=None):
    """ثبت رزرو جدید در دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (name, phone, location, nights, checkin, room_type, notes, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, "در انتظار تایید", datetime('now','localtime'))
    ''', (name, phone, location, nights, str(checkin) if checkin else None, room_type, notes))
    conn.commit()
    conn.close()


def get_all_reservations():
    """دریافت تمام رزروها"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_status(res_id, new_status):
    """تغییر وضعیت رزرو"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE reservations SET status = ? WHERE id = ?', (new_status, res_id))
    conn.commit()
    conn.close()

