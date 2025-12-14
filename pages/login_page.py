
# pages/login_page.py
import streamlit as st
from utils.auth import login_user
import sqlite3

def show(conn):
    st.title("登录 AnPick")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password",key="login_password")
    if st.button("登录"):
        ok = login_user(conn, username, password)
        if ok:
            st.success("登录成功")
            st.rerun()
        else:
            st.error("用户名或密码错误")
    st.write("没有账号？")
    if st.button("注册新账号"):
        st.session_state["page"] = "register"
        st.rerun()
conn = sqlite3.connect("data.db")
show(conn)
