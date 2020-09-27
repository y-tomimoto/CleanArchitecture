from mysql import connector
from werkzeug.exceptions import Conflict, NotFound

# sqlクライアント用のconfig
from enterprise_business_rules.dto.input_memo_dto import MemoData

config = {
    'user': 'root',
    'password': 'password',
    'host': 'mysql',
    'database': 'test_database',
    'autocommit': True
}


class MemoRepository:

    def exist(self, memo_id: int) -> bool:
        # DBクライアントを作成する
        conn = connector.connect(**config)
        cursor = conn.cursor()

        # memo_idがあるかどうか確認する
        query = "SELECT EXISTS(SELECT * FROM test_table WHERE memo_id = %s)"
        cursor.execute(query, [memo_id])
        result: tuple = cursor.fetchone()

        # DBクライアントをcloseする
        cursor.close()
        conn.close()

        # 検索結果が1件あるかどうかで存在を確認する
        if result[0] == 1:
            return True
        else:
            return False

    def get(self, memo_id: int) -> MemoData:

        # 指定されたidがあるかどうか確認する
        is_exist = self.exist(memo_id)

        if not is_exist:
            raise NotFound(f'memo_id [{memo_id}] is not registered yet.')

        # DBクライアントを作成する
        conn = connector.connect(**config)
        cursor = conn.cursor()

        # memo_idで検索を実行する
        query = "SELECT * FROM test_table WHERE memo_id = %s"
        cursor.execute(query, [memo_id])
        result: tuple = cursor.fetchone()

        # DBクライアントをcloseする
        cursor.close()
        conn.close()

        return MemoData(memo_id=memo_id, memo=result[1])

    def save(self, memo_id: int, memo: str) -> bool:

        # 指定されたidがあるかどうか確認する
        is_exist = self.exist(memo_id)

        if is_exist:
            raise Conflict(f'memo_id [{memo_id}] is already registered.')

        # DBクライアントを作成する
        conn = connector.connect(**config)
        cursor = conn.cursor()

        # memoを保存する
        query = "INSERT INTO test_table (memo_id, memo) VALUES (%s, %s)"
        cursor.execute(query, (memo_id, memo))

        # DBクライアントをcloseする
        cursor.close()
        conn.close()

        return True
