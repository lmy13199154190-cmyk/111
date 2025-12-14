# utils/ai_risk.py
import math
from datetime import datetime

def ai_analyze(order):
    """
    订单风险分析函数：基于订单数据计算风险分+分析特征
    :param order: 订单字典（包含id、distance_expected等字段）
    :return: 风险分（0-100）、分析特征字典
    """
    risk_score = 0
    features = {
        "距离异常": "正常",
        "取件超时": "正常",
        "GPS波动": "正常",
        "柜机状态": "正常",
        "照片验证": "正常"
    }

    if order.get("distance_expected") and order.get("distance_actual"):
        dev_ratio = abs(order["distance_actual"] - order["distance_expected"]) / order["distance_expected"]
        if dev_ratio > 0.3:
            risk_score += 30
            features["距离异常"] = f"偏差{dev_ratio:.1%}（高风险）"

    if order.get("pickup_time") and order.get("finish_time"):
        from datetime import datetime
        pickup = datetime.fromisoformat(order["pickup_time"])
        finish = datetime.fromisoformat(order["finish_time"])
        duration = (finish - pickup).total_seconds() / 3600
        if duration > 2:
            risk_score += 25
            features["取件超时"] = f"耗时{duration:.1f}小时（高风险）"

    if order.get("gps_jumps") and order["gps_jumps"] > 5:
        risk_score += 20
        features["GPS波动"] = f"跳变{order['gps_jumps']}次（高风险）"

    if order.get("cabinet_status") != "active":
        risk_score += 15
        features["柜机状态"] = f"当前状态：{order['cabinet_status']}（中风险）"

    if not order.get("photo_ok"):
        risk_score += 10
        features["照片验证"] = "未通过（中风险）"

    risk_score = max(0, min(100, risk_score))
    return risk_score, features

def risk_route_deviation(distance_expected, distance_actual):
    if distance_expected is None or distance_actual is None:
        return 0

    # 偏差率
    deviation = abs(distance_actual - distance_expected) / max(distance_expected, 1)
    score = min(deviation * 100, 100)  # 最大 100 分风险
    return round(score, 1)


def risk_delay(pickup_time, finish_time, expected_minutes=30):
    if not pickup_time or not finish_time:
        return 0

    delta_minutes = (finish_time - pickup_time).total_seconds() / 60
    if delta_minutes <= expected_minutes:
        return 0

    # 超时时长越多，风险越高
    score = min((delta_minutes - expected_minutes) * 2, 100)
    return round(score, 1)


def risk_cabinet_stay(in_time, out_time, max_minutes=5):
    if not in_time or not out_time:
        return 0

    stay = (out_time - in_time).total_seconds() / 60
    if stay <= max_minutes:
        return 0

    return min((stay - max_minutes) * 10, 100)


def risk_gps_jumps(gps_jumps):
    if gps_jumps is None:
        return 0
    return min(gps_jumps * 5, 100)


def risk_photo(photo_ok):
    return 0 if photo_ok == 1 else 50


def calculate_total_risk(route, delay, cabinet, gps, photo):
    # 简单加权
    return round(
        0.4 * route +
        0.3 * delay +
        0.1 * cabinet +
        0.1 * gps +
        0.1 * photo,
        1
    )

def detect_route_deviation(order):
    try:
        distance_actual=float(order.get("distance_actual",0))
    except(ValueError, TypeError):
        return 20,"实际距离数据异常（非数字）"
    try:
        distance_expected=float(order.get("distance_expected",0))
    except(ValueError, TypeError):
        return 20,"预测距离数据异常（非数字）"

    if not distance_expected:
        return 0, "正常"

    dev_ratio = abs(distance_actual - distance_expected) / distance_expected
    if dev_ratio > 0.3:
        return 30, f"路线偏离{dev_ratio:.1%}（高风险）"
    return 0, "正常"


def detect_time_anomaly(order):
    """2. 时间异常检测：超时/停留过久"""
    score = 0
    desc = "正常"
    # 超时未送达（取件后>2小时未完成）
    if order.get("pickup_time") and order.get("finish_time"):
        from datetime import datetime
        pickup = datetime.fromisoformat(order["pickup_time"])
        finish = datetime.fromisoformat(order["finish_time"])
        duration = (finish - pickup).total_seconds() / 3600
        if duration > 2:
            score += 25
            desc = f"超时{duration:.1f}小时（高风险）"
    # 从柜子取走后长时间停留（假设order含cabinet_leave_time字段）
    if order.get("cabinet_leave_time") and order.get("finish_time"):
        leave = datetime.fromisoformat(order["cabinet_leave_time"])
        finish = datetime.fromisoformat(order["finish_time"])
        stay = (finish - leave).total_seconds() / 60
        if stay > 10:
            score += 20
            desc += "；取件后停留过久（中风险）"
    return score, desc


def detect_camera_behavior(order):
    """3. 摄像头行为识别：可疑动作/取件异常"""
    score = 0
    desc = "正常"
    # 可疑动作（假设order含camera_suspicious字段）
    if order.get("camera_suspicious"):
        score += 35
        desc = "检测到可疑动作（高风险）"
    # 未按流程取件
    if order.get("pickup_process") == "abnormal":
        score += 15
        desc += "；未按流程取件（中风险）"
    # 不同人取件（假设order含face_match字段）
    if not order.get("face_match"):
        score += 20
        desc += "；非下单人取件（中风险）"
    return score, desc


def ai_analyze(order):
    risk_score = 0
    features = {}

    # 调用3大模块检测
    route_score, route_desc = detect_route_deviation(order)
    time_score, time_desc = detect_time_anomaly(order)
    camera_score, camera_desc = detect_camera_behavior(order)

    # 汇总风险
    risk_score = route_score + time_score + camera_score
    features["路线异常检测"] = route_desc
    features["时间异常检测"] = time_desc
    features["摄像头行为识别"] = camera_desc

    risk_score = max(0, min(100, risk_score))
    return risk_score, features