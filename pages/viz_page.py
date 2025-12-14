from utils.report import generate_weekly_report
import streamlit as st
import pandas as pd
import sqlite3

def show(conn):
    st.title("📊 数据可视化与周报导出")
    try:
        orders = pd.read_sql("SELECT * FROM orders", conn)
    except Exception as e:
        st.error(f"读取订单数据失败:{str(e)}")
        return
    if "risk_score"not in orders.columns:
        st.warning("订单表中风险评分字段，无法生成风险数据")
        risks=pd.DataFrame()
    else:
        risks=orders[["order_time","risk_score"]].copy()
        risks["order_time"] = pd.to_datetime(orders["order_time"])
        risks["day"]=risks["order_time"].dt.day

    if st.button("📄 生成 本周 周报"):
        if orders.empty:
            st.info("暂无订单数据，无法生成周报")
            return
        try:
            report_path = generate_weekly_report(orders, risks)
            with open(report_path, "r",encoding="utf-8") as f:
                st.download_button(label="下载周报 (文本版)",data=f, file_name="weekly_report.txt",mime="application/txt")
            st.subheader("📈本周订单量图表")
            st.image("orders.png")
            if not risks.empty:
                st.subheader("📉本周风险趋势图表")
                st.image("orders.png")
            st.success("周报生成成功！")
        except Exception as e:
            st.error(f"生成周报失败:{str(e)}")
if __name__ == "__main__":
    conn = sqlite3.connect("data.db")
    show(conn)