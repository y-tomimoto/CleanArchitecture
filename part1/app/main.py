from http import HTTPStatus
from flask import Flask, request, jsonify, make_response
from mysql import connector
from werkzeug.exceptions import Conflict, NotFound

app = Flask(__name__)

# DB接続用の設定
config = {
    'user': 'root',
    'password': 'password',
    'host': 'mysql',
    'database': 'test_database',
    'autocommit': True
}


def exist(memo_id: int) -> bool:
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


@app.route('/memo/<int:memo_id>')
def get(memo_id: int) -> str:
    # 指定されたidがあるかどうか確認する
    is_exist: bool = exist(memo_id)

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

    return jsonify(
        {
            "message": f'memo : [{result[1]}]'
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    # 指定されたidがあるかどうか確認する
    is_exist: bool = exist(memo_id)

    if is_exist:
        raise Conflict(f'memo_id [{memo_id}] is already registered.')

    # リクエストから値を取得する
    memo: str = request.form["memo"]

    # DBクライアントを作成する
    conn = connector.connect(**config)
    cursor = conn.cursor()

    # memoを保存する
    query = "INSERT INTO test_table (memo_id, memo) VALUES (%s, %s)"
    cursor.execute(query, (memo_id, memo))

    # DBクライアントをcloseする
    cursor.close()
    conn.close()

    return jsonify(
        {
            "message": "saved."
        }
    )


@app.errorhandler(NotFound)
def handle_404(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json, HTTPStatus.NOT_FOUND)


@app.errorhandler(Conflict)
def handle_409(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json, HTTPStatus.CONFLICT)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
