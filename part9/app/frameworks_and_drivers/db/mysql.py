from enterprise_business_rules.entity.memo import Memo
from enterprise_business_rules.memo_data import MemoData
from enterprise_business_rules.value_object.memo_author import MemoAuthor
from interface_adapters.gataways.memo_repository_gateway import MemoRepositoryGateway
from werkzeug.exceptions import Conflict, NotFound


class Mysql(MemoRepositoryGateway):

    def __init__(self, connection):
        self.conn = connection

    def exist(self, memo_id: int) -> bool:
        cursor = self.conn.cursor()

        # memo_idがあるかどうか確認する
        query = "SELECT EXISTS(SELECT * FROM test_table WHERE memo_id = %s)"
        cursor.execute(query, [memo_id])
        result: tuple = cursor.fetchone()

        # DBクライアントをcloseする
        cursor.close()

        # 検索結果が1件あるかどうかで存在を確認する
        if result[0] == 1:
            return True
        else:
            return False

    def get(self, memo_id: int) -> Memo:

        # 指定されたidがあるかどうか確認する
        is_exist: bool = self.exist(memo_id)

        if not is_exist:
            raise NotFound(f'memo_id [{memo_id}] is not registered yet.')

        # DBクライアントを作成する
        cursor = self.conn.cursor()

        # memo_idで検索を実行する
        query = "SELECT * FROM test_table WHERE memo_id = %s"
        cursor.execute(query, [memo_id])
        result: tuple = cursor.fetchone()

        # DBクライアントをcloseする
        cursor.close()

        return Memo(memo_id=memo_id, memo=result[1], memo_author=result[2],memo_user_agent=result[3])

    def save(self, m: Memo) -> bool:
        memo_id: int = m.memo_id
        memo: str = m.memo
        memo_author: MemoAuthor = m.memo_author
        memo_user_agent: MemoAuthor = m.memo_user_agent


        # 指定されたidがあるかどうか確認する
        is_exist = self.exist(memo_id)

        if is_exist:
            raise Conflict(f'memo_id [{memo_id}] is already registered.')

        # DBクライアントを作成する
        cursor = self.conn.cursor()

        # memoを保存する
        query = "INSERT INTO test_table (memo_id, memo, memo_author,memo_user_agent) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (memo_id, memo, memo_author, memo_user_agent))

        # DBクライアントをcloseする
        cursor.close()

        return True
