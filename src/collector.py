import yfinance as yf
import pandas as pd
import datetime

def fetch_data(ticker="SPY", period="2y", interval="1d"):
    """
    yfinance를 활용하여 원시 주가 데이터를 가져옵니다.
    """
    print(f"Fetching raw data for {ticker}...")
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    
    # 멀티인덱스 컬럼 처리 (yfinance 최신 버전 대응)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    df.reset_index(inplace=True)
    return df
