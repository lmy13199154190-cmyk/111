# pages/dashboard.py
import streamlit as st
import sqlite3
from utils.db import query
from utils.charts import orders_df, plot_risk_time_distribution, plot_cabinet_heatmap


def show(conn):
    st.title("仪表盘")
    rows = query(conn, "SELECT * FROM orders ORDER BY id DESC", fetch=True)
    df = orders_df(rows)
    if df.empty:
        st.warning("暂无订单数据")
        return
    st.subheader("关键指标")
    st.metric("订单总数", len(df))
    if "risk" in df.columns:
        risk_count=len(df[df["risk"]>0.6])if not df.empty else 0
        st.metric("异常订单（risk>0.6）", risk_count)
    else:
        st.metric("异常订单（risk>0.6)",0)
        st.caption("注:risk列不存在")
    st.subheader("高风险时段")
    fig = plot_risk_time_distribution(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("无法生成时间分布图")
    st.subheader("按柜子汇总风险")
    fig2 = plot_cabinet_heatmap(df)
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("无法生成风险热力图")
conn=sqlite3.connect("data.db")

show(conn)

