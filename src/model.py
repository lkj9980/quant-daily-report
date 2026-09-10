import numpy as np

def generate_signals(df, confidence_threshold=0.65):
    """
    단순 룰 기반 혹은 모멘텀 확률 분포를 산출하여 신호(UP, DOWN, HOLD_CASH)를 생성합니다.
    """
    print("Generating probability distributions and signals...")
    
    signals = []
    confidences = []
    
    for idx, row in df.iterrows():
        # 예시 모멘텀 로직 (실제 머신러닝 모델 예측값으로 대체 가능)
        mom = row['Close'] - row['ma_20']
        
        if pd.isna(mom):
            sig = "HOLD_CASH"
            conf = 0.5
        elif mom > 0:
            sig = "UP"
            conf = 0.75 if row['disparity_5'] < 3.0 else 0.55  # 과매수 구간 신뢰도 하향 조정
        else:
            sig = "DOWN"
            conf = 0.70
            
        # 신뢰도 임계값 적용 (무매매 구간 필터링)
        if conf < confidence_threshold:
            sig = "HOLD_CASH (No-Action Zone)"
            
        signals.append(sig)
        confidences.append(conf)
        
    df['signal'] = signals
    df['confidence'] = confidences
    return df
