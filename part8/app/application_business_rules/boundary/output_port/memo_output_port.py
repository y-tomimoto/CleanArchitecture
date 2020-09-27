from abc import ABC, abstractmethod

from enterprise_business_rules.dto.output_memo_dto import OutputMemoDTO


class MemoOutputPort(ABC):
    @abstractmethod
    def create_view_for_get(self, output_memo_dto: OutputMemoDTO) -> str:
        pass

    @abstractmethod
    def create_view_for_save(self, output_memo_dto: OutputMemoDTO) -> str:
        pass

    @abstractmethod
    def create_view_for_get_by_day(self, output_memo_dto: OutputMemoDTO) -> str:
        pass