import streamlit as st
from utils.db import query
from utils.ai_service import analyze_and_save
import sqlite3

def show(conn):

    st.title("🧠 AI 风险检测系统（Anti-Theft AI）")

    st.markdown("系统会自动分析订单行为并给出风险评分。")

    orders = query(conn, "SELECT * FROM orders ORDER BY id DESC", fetch=True)

    if not orders:
        st.info("暂无订单数据")
        return

    st.subheader("选择要分析的订单")

    selected_order_id = st.selectbox(
        "请选择订单",
        options=[o[0] for o in orders],
        format_func=lambda x: f"订单 #{x}"
    )

    order_row = next((o for o in orders if o[0] == selected_order_id), None)
    if order_row:
        order = {
            "id": order_row[0],
            "distance_expected": order_row[3],
            "distance_actual": order_row[4],
            "pickup_time": order_row[5],
            "finish_time": order_row[6],
            "cabinet_status": order_row[2],
            "gps_jumps": order_row[7],
            "photo_ok": order_row[8],
        }

        if st.button("开始 AI 分析"):

            score, features = analyze_and_save(conn, order)
            st.success(f"分析完成！风险评分：**{score:.2f} / 100**")

            st.subheader("📊AI行为检测模块结果")
            with st.expander("1.路线异常检测"):
                st.write(features["路线异常检测"])
                if "高风险"in features["路线异常检测"]:
                    st.error("⚠️路线偏离度过高")

            with st.expander("2.时间异常检测"):
                st.write(features["时间异常检测"])
                if "高风险"in features["时间异常检测"]:
                    st.error("⚠️存在超时/停留时间过久行为")

            with st.expander("3.摄像头行为识别"):
                st.write(features["摄像头行为识别"])
                if "高风险"in features["摄像头行为识别"]:
                    st.error("⚠️检测到可疑行为")

            st.divider()
            st.subheader("风险等级")
            if score >= 80:
                st.error("⚠️ 高风险订单！可能存在外卖被偷或违规配送行为。")
            elif score >= 60:
                st.warning("⚠️ 可疑订单，建议客服复核。")
            else:
                st.info("订单正常。")

        st.divider()

        st.subheader("📜 历史风控记录")

        logs = query(conn, "SELECT * FROM ai_risk_logs ORDER BY id DESC LIMIT 20", fetch=True)

        if logs:
            st.table(logs)
        else:
            st.write("暂无记录")
if __name__ == "__main__":
    conn = sqlite3.connect("data.db")
    show(conn)
