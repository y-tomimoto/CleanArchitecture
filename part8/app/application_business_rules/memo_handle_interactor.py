import datetime
from werkzeug.exceptions import NotFound

from application_business_rules.boundary.output_port.memo_output_port import MemoOutputPort
from enterprise_business_rules.dto.input_memo_dto import InputMemoDTO
from enterprise_business_rules.dto.output_memo_dto import OutputMemoDTO
from enterprise_business_rules.entity.memo import Memo
from enterprise_business_rules.value_object.memo_author import MemoAuthor
from interface_adapters.gataways.memo_repository_gateway import MemoRepositoryGateway


class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
        m: Memo = self.repository.get(memo_id)
        output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id, memo=m.memo,
                                              memo_author=m.memo_author)
        return self.presenter.create_view_for_get(output)

    def save(self, input_memo_dto: InputMemoDTO):
        m = Memo(memo_id=input_memo_dto.memo_id, memo=input_memo_dto.memo, memo_author=MemoAuthor(input_memo_dto.memo_author),
                 memo_user_agent=input_memo_dto.memo_user_agent)
        self.repository.save(m)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:

            m: Memo = self.repository.get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id, memo=m.memo,
                                              memo_author=m.memo_author)

        return self.presenter.create_view_for_get_by_day(output)
