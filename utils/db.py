import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "data.db"   # 你项目的数据库文件名


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # 1. 用户表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    );
    """)

    # 自动创建管理员账号
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", admin_pass, "admin"))
        print("管理员账号已创建：账号 admin / 密码 admin123")

    # 2. 订单表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    user_id INTEGER,
    courier_id INTEGER,
    cabinet_id INTEGER,
    order_time TIMESTAMP,
    delivery_time TIMESTAMP,
    in_cabinet_time TIMESTAMP,
     out_cabinet_time TIMESTAMP,
    status TEXT,
    risk_score REAL DEFAULT 0,
    notes TEXT,
    
    
    distance_expected REAL,
    distance_actual REAL,
    pickup_time TIMESTAMP,
    finish_time TIMESTAMP,
    gps_jumps INTEGER,
    photo_ok INTEGER DEFAULT 1


    );
    """)

    cur.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
            camera_id TEXT PRIMARY KEY,
            cabinet_id TEXT,
            location TEXT,
            status TEXT
            );
        """)
    # 3. 柜子表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cabinets (
    cabinet_id TEXT PRIMARY KEY,
    location TEXT,
    status TEXT

    );
    """)

    # 4. AI 风控日志表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_risk_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        risk_score REAL,
        route_deviation REAL,
        delay_risk REAL,
        cabinet_risk REAL,
        gps_risk REAL,
        photo_risk REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    return conn



# --- 通用查询函数 ---
def query(conn, sql, params=(), fetch=False):
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    if fetch:
        return cur.fetchall()
