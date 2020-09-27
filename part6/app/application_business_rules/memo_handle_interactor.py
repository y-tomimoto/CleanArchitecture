import datetime
from werkzeug.exceptions import NotFound

from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from enterprise_business_rules.dto.input_memo_dto import MemoData
from enterprise_business_rules.entity.memo import MemoRepository


class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort):
        self.presenter = presenter

    def get(self, memo_id: int) -> str:
        result: MemoData = MemoRepository().get(memo_id)
        return self.presenter.create_view_for_get(result)

    def save(self, memo_object: MemoData) -> str:
        MemoRepository().save(memo_object)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
            result: MemoData = MemoRepository().get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        return self.presenter.create_view_for_get_by_day(result)
