from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from enterprise_business_rules.memo_data import MemoData


class DefaultPresenter(MemoOutputPort):

    def create_view_for_get(self, memo_data: MemoData):
        return f'memo : [{memo_data.memo}]'

    def create_view_for_save(self):
        return f'saved.'

    def create_view_for_get_by_day(self, memo_data: MemoData):
        return f'本日のメモは [{memo_data.memo}] です!'
