import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .config import FEATURED_MIN_STARS, FEATURED_TAG, UID_DOMAIN


@dataclass
class CalendarItem:
    """一条待写入日历的日程。"""

    kind: str
    title: str
    country: str
    stars: int
    tag: str
    moment: Optional[datetime]
    clock: str
    body: str
    source_id: str = ""

    @property
    def is_featured(self) -> bool:
        return self.stars >= FEATURED_MIN_STARS or self.tag == FEATURED_TAG

    @property
    def sort_key(self) -> datetime:
        return self.moment or datetime(1970, 1, 1)

    @property
    def uid(self) -> str:
        """稳定 UID：优先用上游 id，缺失时退回内容哈希，保证重跑不变。"""
        if self.source_id:
            return f"{self.kind}-{self.source_id}@{UID_DOMAIN}"
        fingerprint = f"{self.kind}|{self.moment}|{self.clock}|{self.title}|{self.country}"
        digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:20]
        return f"{digest}@{UID_DOMAIN}"
