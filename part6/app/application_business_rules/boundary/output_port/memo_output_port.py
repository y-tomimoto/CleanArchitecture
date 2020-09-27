from abc import ABC, abstractmethod

from enterprise_business_rules.dto.input_memo_dto import MemoData


class MemoOutputPort(ABC):
    @abstractmethod
    def create_view_for_get(self, memo_memo: MemoData) -> str:
        pass

    @abstractmethod
    def create_view_for_save(self, memo_memo: MemoData) -> str:
        pass

    @abstractmethod
    def create_view_for_get_by_day(self, memo_memo: MemoData) -> str:
        pass
