from dataclasses import dataclass


@dataclass
class MemoData:
    memo_id: int
    memo: str
    memo_author: str
