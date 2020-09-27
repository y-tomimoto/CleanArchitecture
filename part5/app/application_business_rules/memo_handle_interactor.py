import datetime

from werkzeug.exceptions import NotFound

from enterprise_business_rules.dto.input_memo_dto import MemoData
from enterprise_business_rules.entity.memo import MemoRepository


class MemoHandleInteractor:
    def get(self, memo_id):
        result: MemoData = MemoRepository().get(memo_id)
        return f'memo : [{result.memo}]'

    def save(self, memo_object: MemoData):
        MemoRepository().save(memo_object)
        return 'saved.'

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
            result: MemoData = MemoRepository().get(day_number)
        except NotFound:
            return f'本日 [{day_number}] 日のメモはまだ登録されていません。'

        return f'本日のメモは [{result.memo}] です!'
