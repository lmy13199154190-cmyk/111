# utils/auth.py
import hashlib
import streamlit as st
import sqlite3

def hash_password(password: str) -> str:
    if password is None:
        return ""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(conn: sqlite3.Connection, username: str, password: str, role: str = "user"):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"
    except Exception as e:
        return False, f"注册失败: {e}"

def login_user(conn: sqlite3.Connection, username: str, password: str):
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if row and hash_password(password) == row[2]:
        user = {"id": row[0], "username": row[1], "role": row[3]}
        st.session_state["user"] = user
        return True
    return False

def current_user():
    return st.session_state.get("user", None)

def logout_user():
    if "user" in st.session_state:
        del st.session_state["user"]