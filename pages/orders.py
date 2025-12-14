# pages/orders.py 修正后

import streamlit as st
from utils.db import query
from utils.risk import compute_risk
from datetime import datetime
import sqlite3

def show(conn):
    st.title("订单管理")
    
    # 使用会话状态存储 order_id，防止输入框每次刷新都变化
    if 'temp_order_id' not in st.session_state:
        st.session_state.temp_order_id = f"order_{int(datetime.utcnow().timestamp())}"

    with st.expander("新增模拟订单（用于演示）"):
        # 移除了 order_id 的自动更新逻辑，改用 session_state
        order_id = st.text_input("Order ID", value=st.session_state.temp_order_id)
        user_id = st.text_input("用户ID", value="user1")
        courier_id = st.text_input("配送员ID", value="courier1")
        cabinet_id = st.text_input("柜子编号", value="3.2")
        
        # 关键修改：将数据库操作移入按钮的 if 块内
        # /pages/orders.py (修正后的 if 块)

# ... 省略部分代码 ...
        if st.button("生成入柜订单"):
            now = datetime.utcnow().isoformat()
            
            # --- 【修正点 2】: 修正 SQL 语句和参数列表 ---
            conn.execute(
                """
                INSERT INTO orders (
                    order_id,
                    user_id,
                    courier_id,
                    cabinet_id,
                    in_cabinet_time,
                    out_cabinet_time,
                    status,
                    risk_score,
                    distance_expected,
                    distance_actual
                )
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                # 必须严格按顺序提供 10 个值 (对应上面的 10 个字段)
                (
                    order_id,     # order_id
                    user_id,      # user_id
                    courier_id,   # courier_id
                    cabinet_id,   # cabinet_id
                    now,          # in_cabinet_time (使用 now)
                    None,         # out_cabinet_time (使用 None)
                    "in",         # status
                    0.0,          # risk_score (初始为 0.0)
                    2.5,          # distance_expected (使用 2.5)
                    0.0           # distance_actual (使用 0.0)
                )
            )
            conn.commit()
            # ... 省略部分代码 ...
            st.success("模拟订单已创建")
                
                # 更新 order_id 以便下次创建新订单
                st.session_state.temp_order_id = f"order_{int(datetime.utcnow().timestamp())}"
                st.rerun() # 重新运行以刷新界面和订单列表

            except sqlite3.IntegrityError:
                st.error(f"订单ID {order_id} 已存在，请修改后再试。")

    
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

conn = sqlite3.connect("data.db", check_same_thread=False) # 建议增加 check_same_thread=False
show(conn)


