# pages/orders.py
import streamlit as st
from utils.db import query
from utils.risk import compute_risk
from datetime import datetime
import sqlite3

def show(conn):
    st.title("订单管理")
    with st.expander("新增模拟订单（用于演示）"):
        order_id = st.text_input("Order ID", value=f"order_{int(datetime.utcnow().timestamp())}")
        user_id = st.text_input("用户ID", value="user1")
        courier_id = st.text_input("配送员ID", value="courier1")
        cabinet_id = st.text_input("柜子编号", value="3.2")
        if st.button("生成入柜订单"):
            now = datetime.utcnow().isoformat()
            conn.execute("""INSERT INTO orders (order_id,user_id,courier_id,cabinet_id,in_cabinet_time,out_cabinet_time,status,risk,distance_actual,distance_expected))
                            VALUES (?,?,?,?,?,?,?,?,?,?)""",
                         (order_id,user_id,courier_id,3.5,now,now,now,"in",0.0,cabinet_id,2.5))
            conn.commit()


            st.success("模拟订单已创建")
    st.write("---")
    rows = query(conn, "SELECT * FROM orders ORDER BY id DESC", fetch=True)
    if not rows:
        st.info("暂无订单")
        return
    for r in rows[:50]:
        st.write({
            "id": r[0],"order_id":r[1],"user_id":r[2],"courier_id":r[3],
            "cabinet_id":r[4],"in":r[7],"out":r[8],"status":r[9],"risk":r[10]
        })
        cols = st.columns([1,1,1,1])
        if cols[0].button("标记出柜", key=f"out_{r[0]}"):
            now = datetime.utcnow().isoformat()
            conn.execute("UPDATE orders SET out_cabinet_time=?, status=? WHERE id=?", (now,"completed", r[0]))
            conn.commit()
            st.success("已标记出柜")
            st.rerun()
        if cols[1].button("重新评估风险", key=f"re_risk_{r[0]}"):
            # fetch row
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders WHERE id=?", (r[0],))
            row = cur.fetchone()
            order = {
                "in_cabinet_time": row[7],
                "out_cabinet_time": row[8],
                "notes": row[11] if row[11] else ""
            }
            score = compute_risk(order)
            conn.execute("UPDATE orders SET risk_score=? WHERE id=?", (score, r[0]))
            conn.commit()
            st.success(f"风险评分更新为 {score:.2f}")
            st.rerun()
conn = sqlite3.connect("data.db")
show(conn)
