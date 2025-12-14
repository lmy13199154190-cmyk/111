from utils.db import query
from utils.ai_risk import ai_analyze

def save_risk_result(conn, order_id, score, features):
    sql="""
    INSERT INTO ai_risk_logs(order_id, risk_score,route_deviation,delay_risk,cabinet_risk,gps_risk,photo_risk) VALUES (?,?,?,?,?,?,?)"""
    params=(order_id,score,features.get('route_deviation'),features.get('delay_risk'),features.get('cabinet_risk'),features.get('gps_risk'),features.get('photo_risk'))
    query(conn, sql, params=params)

def analyze_and_save(conn, order):
    score, features = ai_analyze(order)
    save_risk_result(conn, order["id"], score, features)
    return score, features
