# pages/register_page.py
import streamlit as st
from utils.auth import register_user
import sqlite3

def show(conn):
    st.title("注册 AnPick 账号")
    username = st.text_input("用户名（学号/工号）")
    password = st.text_input("密码", type="password")
    role = st.selectbox("角色", ["user","courier","staff","admin"])
    if st.button("注册"):
        ok,msg = register_user(conn, username, password, role)
        if ok:
            st.success(msg + "，请返回登录。")
        else:
            st.error(msg)
    if st.button("返回登录"):
        st.session_state["page"] = "login"
        st.rerun()
conn = sqlite3.connect("data.db")
show(conn)