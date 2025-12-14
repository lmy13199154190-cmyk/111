# pages/dashboard.py
import streamlit as st
import sqlite3
from utils.db import query
from utils.charts import orders_df, plot_risk_time_distribution, plot_cabinet_heatmap


def show(conn):
    st.title("仪表盘")
    rows = query(conn, "SELECT * FROM orders ORDER BY id DESC", fetch=True)
    df = orders_df(rows)
    st.subheader("关键指标")
    st.metric("订单总数", len(df))
    st.metric("异常订单（risk>0.6）", len(df[df["risk"]>0.6]) if not df.empty else 0)
    st.subheader("高风险时段")
    fig = plot_risk_time_distribution(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("按柜子汇总风险")
    fig2 = plot_cabinet_heatmap(df)
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
conn=sqlite3.connect("data.db")
show(conn)