import pandas as pd
import numpy as np

def build_features(price_df, macro_df):
    # 고주파수 팩터 (예: 5일/20일 이격도)
    price_df['ma_5'] = price_df['close'].rolling(5).mean()
    price_df['disparity_5'] = (price_df['close'] - price_df['ma_5']) / price_df['ma_5'] * 100
    
    # 저주파수 레짐 필터 통합
    merged = pd.merge(price_df, macro_df, on='date', how='left').ffill()
    return merged
