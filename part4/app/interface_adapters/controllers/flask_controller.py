from application_business_rules.memo_handle_interactor import MemoHandleInteractor
from flask import request


class FlaskController:

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor().get(memo_id)

    def save(self, memo_id: int, request: request) -> str:
        # memo = request.form["memo"]
        memo: str = request.json["memo"]
        return MemoHandleInteractor().save(memo_id, memo)

    def get_by_day_number(self) -> str:
        return MemoHandleInteractor().get_by_day_number()