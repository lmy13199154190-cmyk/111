# utils/risk.py
from datetime import datetime
from dateutil import parser

def compute_risk(order):
    """
    Simple rule-based risk scoring.
    order: dict-like with keys in_cabinet_time, out_cabinet_time, notes (can contain open_count)
    Returns risk_score in [0,1]
    """
    score = 0.0
    # quick take rule: out - in < 10 seconds => suspicious
    try:
        if order.get("in_cabinet_time") and order.get("out_cabinet_time"):
            t_in = parser.parse(order["in_cabinet_time"])
            t_out = parser.parse(order["out_cabinet_time"])
            delta = (t_out - t_in).total_seconds()
            if delta < 10:
                score = max(score, 0.9)
            elif delta < 60:
                score = max(score, 0.6)
    except Exception:
        pass

    # long wait rule: in -> no out for > 2 hours
    try:
        if order.get("in_cabinet_time") and not order.get("out_cabinet_time"):
            t_in = parser.parse(order["in_cabinet_time"])
            delta = (datetime.utcnow() - t_in).total_seconds()
            if delta > 7200:  # 2 hours
                score = max(score, 0.7)
    except Exception:
        pass

    # note-based repeated opens (if notes includes open_count)
    try:
        open_count = int(order.get("notes","0").count("open=")) if order.get("notes") else 0
        # fallback: parse "open_count:3" style
        if "open_count:" in (order.get("notes") or ""):
            parts = (order.get("notes") or "").split("open_count:")
            try:
                oc = int(parts[1].split()[0])
                open_count = oc
            except:
                pass
        if open_count >= 3:
            score = max(score, 0.8)
    except Exception:
        pass

    # normalize
    return float(score)