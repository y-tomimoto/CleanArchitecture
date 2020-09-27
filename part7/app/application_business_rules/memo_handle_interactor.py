import datetime
from werkzeug.exceptions import NotFound

from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from enterprise_business_rules.memo_data import MemoData
from interface_adapters.gataways.memo_repository_gateway import MemoRepositoryGateway


class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
        result: MemoData = self.repository.get(memo_id)
        return self.presenter.create_view_for_get(result)

    def save(self, memo_data: MemoData):
        self.repository.save(memo_data)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
            result: MemoData = self.repository.get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        return self.presenter.create_view_for_get_by_day(result)
