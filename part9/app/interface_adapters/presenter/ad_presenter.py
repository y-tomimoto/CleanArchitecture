from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from enterprise_business_rules.memo_data import MemoData


class AdPresenter(MemoOutputPort):
    def __init__(self):
        self.ad_message = "今なら70円引き!!XXXXマート!!"

    def create_view_for_get(self, memo_data: MemoData):
        return f'memo : [{memo_data.memo}] (ad : {self.ad_message})'

    def create_view_for_save(self):
        return f'saved. (ad : {self.ad_message})'

    def create_view_for_get_by_day(self, memo_data: MemoData):
        return f'本日のメモは [{memo_data.memo}] です!(ad : {self.ad_message})'
