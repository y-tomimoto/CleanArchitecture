from application_business_rules.memo_handle_interactor import MemoHandleInteractor
from flask import request

from enterprise_business_rules.dto.input_memo_dto import MemoData


class FlaskController:

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor().get(memo_id)

    def save(self, memo_id: int, request: request) -> str:
        memo: str = request.json["memo"]
        memo_author: str = request.json["memo_author"]
        memo_object: MemoData = MemoData(memo_id, memo, memo_author)
        return MemoHandleInteractor().save(memo_object)

    def get_by_day_number(self) -> str:
        return MemoHandleInteractor().get_by_day_number()