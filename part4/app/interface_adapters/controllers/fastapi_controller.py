from application_business_rules.memo_handle_interactor import MemoHandleInteractor
from flask import request


class FlaskController:

    def get(self, memo_id: int):
        return MemoHandleInteractor().get(memo_id)

    def save(self, memo_id: int, request: request):
        # memo = request.form["memo"]
        memo = request.json["memo"]
        return MemoHandleInteractor().save(memo_id, memo)

