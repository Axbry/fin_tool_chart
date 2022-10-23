import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FinToolMovement:
    ticker: str
    movement: int
    timestamp: datetime
    price: int

    def to_json(self):
        return json.dumps({
            'ticker': self.ticker,
            'movement': self.movement,
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'price': self.price
        })