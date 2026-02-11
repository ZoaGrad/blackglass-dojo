# nodes/Predictor.py
import pandas as pd
import numpy as np

class Predictor:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, df: pd.DataFrame) -> str:
        """
        Input: DataFrame with 'close' column (OHLCV mock or real)
        Output: 'BUY', 'SELL', 'HOLD'
        """
        if len(df) < self.long_window:
            return 'HOLD'

        df = df.copy()
        df['sma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['sma_long'] = df['close'].rolling(window=self.long_window).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        if latest['sma_short'] > latest['sma_long'] and prev['sma_short'] <= prev['sma_long']:
            return 'BUY'
        elif latest['sma_short'] < latest['sma_long'] and prev['sma_short'] >= prev['sma_long']:
            return 'SELL'
        else:
            return 'HOLD'
