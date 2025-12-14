# app.py

import streamlit as st

# 必须最先初始化数据库（在导入页面之前）
from utils.db import init_db, query
con = init_db()

# 再导入剩余模块（否则它们会提前执行 SQL）
from utils.auth import current_user, logout_user
import pages.login_page as login_page
import pages.register_page as register_page
import pages.dashboard as dashboard
import pages.orders as orders_page
import pages.risk_page as risk_page
import pages.config_page as config_page

# 页面设置
st.set_page_config(page_title="AnPick MIS", layout="wide")

# 默认页面
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# sidebar
st.sidebar.title("AnPick 管理系统")

user = current_user()

# ---------------------------------------
# 未登录
# ---------------------------------------
if not user:
    if st.session_state["page"] == "login":
        login_page.show(con)
    elif st.session_state["page"] == "register":
        register_page.show(con)
    st.stop()

# ---------------------------------------
# 已登录显示侧边栏导航
# ---------------------------------------
st.sidebar.markdown(f"**已登录：** {user['username']} \n**角色：** {user['role']}")

menu = st.sidebar.selectbox(
    "导航",
    ["仪表盘", "订单管理", "风险监控", "系统配置", "登出"]
)

if menu == "仪表盘":
    dashboard.show(con)

elif menu == "订单管理":
    orders_page.show(con)

elif menu == "风险监控":
    risk_page.show(con)

elif menu == "系统配置":
    config_page.show(con)

elif menu == "登出":
    logout_user()
    st.rerun()
