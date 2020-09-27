from abc import abstractmethod, ABCMeta

from enterprise_business_rules.memo_data import MemoData


class MemoRepositoryGateway(metaclass=ABCMeta):
    @abstractmethod
    def get(self, memo_id: str) -> MemoData:
        pass

    @abstractmethod
    def save(self, memo_data: MemoData) -> MemoData:
        pass

    @abstractmethod
    def exist(self, memo_id: str) -> bool:
        pass
