from abc import ABC, abstractmethod

from enterprise_business_rules.dto.input_memo_dto import InputMemoDTO


class MemoInputPort(ABC):
    @abstractmethod
    def get(self, input_memo_dto: InputMemoDTO) -> str:
        pass

    @abstractmethod
    def save(self, input_memo_dto: InputMemoDTO) -> str:
        pass

    @abstractmethod
    def get_by_day_number(self) -> str:
        pass
