# pages/config_page.py
import streamlit as st
from utils.db import query
import sqlite3

def show(conn):
    st.title("系统配置")
    st.subheader("柜子管理")
    if st.button("新增示例柜子"):
        conn.execute("INSERT OR IGNORE INTO cabinets (cabinet_id,location,status) VALUES (?,?,?)", ("3.2","宿舍区A","active"))
        conn.commit()
        st.success("已新增示例柜子")
    rows = query(conn, "SELECT * FROM cabinets", fetch=True)
    st.table(rows)
    st.subheader("摄像头管理")
    if st.button("新增示例摄像头"):
        conn.execute("INSERT OR IGNORE INTO cameras (camera_id,cabinet_id,location,status) VALUES (?,?,?,?)", ("CAM1","C1","门口","online"))
        conn.commit()
        st.success("已新增示例摄像头")
    cams = query(conn, "SELECT * FROM cameras", fetch=True)
    st.table(cams)
conn=sqlite3.connect("data.db")
show(conn)