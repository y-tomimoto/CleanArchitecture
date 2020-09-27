from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from application_business_rules.memo_handle_interactor import MemoHandleInteractor
from flask import request

from enterprise_business_rules.memo_data import MemoData
from interface_adapters.gataways.memo_repository_gateway import MemoRepositoryGateway


class FlaskController:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor(self.presenter, self.repository).get(memo_id)

    def save(self, memo_id: int, request: request) -> str:
        memo: str = request.json["memo"]
        memo_author: str = request.json["memo_author"]
        memo_data: MemoData = MemoData(memo_id, memo, memo_author)

        return MemoHandleInteractor(self.presenter, self.repository).save(memo_data)

    def get_by_day_number(self) -> str:
        return MemoHandleInteractor(self.presenter, self.repository).get_by_day_number()
