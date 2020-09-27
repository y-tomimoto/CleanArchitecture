from dataclasses import dataclass


@dataclass
class InputMemoDTO:
    memo_id: int
    memo: str
    memo_author: str
    memo_user_agent: str
