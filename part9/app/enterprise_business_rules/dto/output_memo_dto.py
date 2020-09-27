from dataclasses import dataclass


@dataclass
class OutputMemoDTO:
    memo_id: int
    memo: str
    memo_author: str
