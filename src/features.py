import pandas as pd
import numpy as np

def build_features(price_df, macro_df=None):
    """
    가격 시퀀스로부터 고주파수 알파 팩터 및 저주파수 레짐 필터를 계산·통합합니다.
    """
    print("Building quantitative features with macro regime integration...")
    df = price_df.copy()
    
    # 1. 고주파수 알파 팩터 (이격도, 이동평균, 변동성 등)
    df['ma_5'] = df['Close'].rolling(5).mean()
    df['ma_20'] = df['Close'].rolling(20).mean()
    df['disparity_5'] = (df['Close'] - df['ma_5']) / df['ma_5'] * 100
    # 변동성 및 수익률
    df['returns'] = df['Close'].pct_change()
    df['volatility_10'] = df['returns'].rolling(10).std() * np.sqrt(252) * 100
    
    # 2. 저주파수 레짐 필터 통합 (매크로 데이터가 제공된 경우)
    if macro_df is not None and not macro_df.empty:
        # 날짜 컬럼명 표준화 (필요시 조정)
        if 'Date' in df.columns and 'date' in macro_df.columns:
            macro_df = macro_df.rename(columns={'date': 'Date'})
        
        df = pd.merge(df, macro_df, on='Date', how='left').ffill()
        print("Macro regime data merged successfully.")
    else:
        # 매크로 데이터가 없을 경우 기본 레짐 필터 컬럼 생성 (예시)
        df['macro_regime'] = np.where(df['Close'] > df['ma_20'], 'BULL', 'BEAR')
    
    df.dropna(inplace=True)
    return df
