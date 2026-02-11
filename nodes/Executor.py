# nodes/Executor.py
class Executor:
    def __init__(self):
        self.position = 0.0  # BTC held
        self.cash = 100000.0  # Starting principal USD
        self.equity = self.cash
        self.peak_equity = self.equity
        self.trades = []  # log: {'time':, 'action':, 'price':, 'size':, ...}

    def execute(self, signal: str, price: float):
        if signal == 'BUY' and self.cash > 0:
            size = self.cash / price
            self.position += size
            self.cash = 0
            self.trades.append({'action': 'BUY', 'price': price, 'size': size})
        elif signal == 'SELL' and self.position > 0:
            self.cash += self.position * price
            # Note: in user's skeleton, this was self.position = 0, but added cash first.
            # Fixed the logic slightly for correctness.
            sell_size = self.position
            self.position = 0
            self.trades.append({'action': 'SELL', 'price': price, 'size': sell_size})

        self.equity = self.cash + self.position * price
        self.peak_equity = max(self.peak_equity, self.equity)
