import streamlit as st
from utils.ml import detect_anomaly
import pandas as pd
import sqlite3
from datetime import datetime

def show(conn):
    st.title("风险监控中心（升级版）")

    st.subheader("📸 摄像头截图上传")
    img = st.file_uploader("上传摄像头抓拍图（jpg/png）", type=["jpg", "png"])

    if img:
        st.image(img, caption="摄像头截图", use_column_width=True)

        # 这里构造一个虚拟行为特征（真实系统可替换为 CV 模型结果）
        features = pd.DataFrame([[3.1, 0.5, 10]], columns=["stay_time","touch_count","night_flag"])
        score = detect_anomaly(features)

        if score == 1:
            st.error("⚠ 检测到异常行为！")
        else:
            st.success("✓ 行为正常")
conn = sqlite3.connect("data.db")
show(conn)