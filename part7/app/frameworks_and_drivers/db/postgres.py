# sqlクライアント用のconfig
from enterprise_business_rules.memo_data import MemoData
from interface_adapters.gataways.memo_repository_gateway import MemoRepositoryGateway
from werkzeug.exceptions import Conflict, NotFound


class PostgreSQL(MemoRepositoryGateway):

    def __init__(self, connection):
        self.conn = connection
        self.conn.autocommit = True

    def exist(self, memo_id) -> bool:

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

    def get(self, memo_id: int) -> MemoData:

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

        return MemoData(memo_id=memo_id, memo=result[1], memo_author=result[2])

    def save(self, memo_data: MemoData) -> bool:
        memo_id: int = memo_data.memo_id
        memo: str = memo_data.memo
        memo_author = memo_data.memo_author

        # 指定されたidがあるかどうか確認する
        is_exist = self.exist(memo_id)

        if is_exist:
            raise Conflict(f'memo_id [{memo_id}] is already registered.')

        # DBクライアントを作成する
        cursor = self.conn.cursor()

        # memoを保存する
        query = "INSERT INTO test_table (memo_id, memo, memo_author) VALUES (%s, %s, %s)"
        cursor.execute(query, (memo_id, memo, memo_author))

        # DBクライアントをcloseする
        cursor.close()

        return True
