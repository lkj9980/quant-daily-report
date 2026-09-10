import pandas as pd
import numpy as np

def build_features(price_df, macro_df):
    """
    가격 시퀀스로부터 고주파수 알파 팩터 및 기술적 지표를 계산합니다.
    """
    print("Building quantitative features...")
    df = price_df.copy()
    
    # 이격도 및 이동평균 계산
    df['ma_5'] = df['Close'].rolling(5).mean()
    df['ma_20'] = df['Close'].rolling(20).mean()
    df['disparity_5'] = (df['Close'] - df['ma_5']) / df['ma_5'] * 100
    
    # 변동성 및 수익률
    df['returns'] = df['Close'].pct_change()
    df['volatility_10'] = df['returns'].rolling(10).std() * np.sqrt(252) * 100
    
    df.dropna(inplace=True)
    
    # 저주파수 레짐 필터 통합
    merged = pd.merge(price_df, macro_df, on='date', how='left').ffill()
    return merged
