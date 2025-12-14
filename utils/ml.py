from sklearn.ensemble import IsolationForest
import numpy as np

# 模拟已训练的模型（真实系统要用历史数据训练）
model = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
model.fit([[1,0,0],[2,1,0],[3,0,1],[10,5,1]])   # 示例训练数据

def detect_anomaly(df):
    pred = model.predict(df)
    return pred[0]   # -1 = 异常，1 = 正常