from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class Product:
    name: str
    price: int | None
    rating: float | None
    reviews: int
    url: str
    marketplace: str = "Ozon"

    def to_dict(self):
        return self.__dict__


class AnalysisResult:
    def __init__(self, product: Product, risk_score: int, verdict: str,
                 emoji: str, risk_level: str, flags: List[str], good: List[str]):
        self.product = product
        self.risk_score = risk_score
        self.verdict = verdict
        self.emoji = emoji
        self.risk_level = risk_level
        self.flags = flags
        self.good = good
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")