# シンプルな API に CleanArchitecture を段階的に適用し、CleanArchitectureが具体的に「どんな変更に強いのか」をコードベースで理解してみる

# 目次
#### [Part1: ベースとなるシンプルな API を作成する](TODO:URLを追加)
#### [Part2: Frameworks & Drivers 層: Web の登場](TODO:URLを追加)
#### [Part3: Enterprise Business Rules 層 & Application Business Rules 層の登場](TODO:URLを追加)
#### [Part4: Interface Adapters 層: Controllers の登場](TODO:URLを追加)
#### [Part5: ~番外編~ DTOの活用](TODO:URLを追加)
#### [Part6: Interface Adapters 層: Presenter の登場](TODO:URLを追加)
#### [Part7: Frameworks & Drivers 層: DB と Interface Adapters 層: Gateways の登場](TODO:URLを追加)
#### [Part8: Enterprise Business Rules 層: Entity & Value Object の採用](TODO:URLを記載)
#### [Part9: テスト可能~まとめ](TODO:URLを記載)

# なぜこの記事を書くか 

最近、技術的にチャレンジさせてもらえるプロジェクトにアサインさせてもらえたので、CleanArchitectureを採用してみました。

採用した際に学んだことを、改めて言語化しておきたいなと思ったのと、

実装していたとき、各レイヤーが解決する課題が、コードベースで解説されている記事があったら捗ったなと思ったので、

この記事を書くことにしました。

## どのような構成で記事を書くか

前述しましたが、現在CleanArchitectureについて世の中に公開されている記事は、
下記の2部構成であることが多いなと個人的に思っています。

1. *CleanArchitectureで作った成果物のコードはこんな感じです。*
2. *〇〇のコードは〇〇レイヤーに対応していて、〇〇レイヤーはこういう役割をしています。*

---

**「CleanArchitectureが具体的にどういう変更に強いのか」** をイメージするにあたり、

冒頭から既に完成された成果物のコードを提示する構成ではなく、

1. *既存の成果物が仕様変更の際に抱える課題を、段階的に解決していく*
2. *最終的に `CleanArchitecture` の構成になっている*

という構成にしようと思います。

## 各Partのストーリーについて

今回記事内で明らかにしたいことは、

**「CleanArchitectureが具体的にどういう変更に強いのか」**

です。

なので、記事内では、下記のような展開で、CleanArchitectureを適用していきます。

*1. 既存の成果物に対して、「○○を追加・変更して欲しい」等の仕様変更依頼を受ける*

*2. 既存の成果物の設計で、仕様変更依頼に対応する際に、どのような懸念点があるかを、コードベースで明示する* 

*3. 仕様変更依頼に対して、どのような設計になっていたら、懸念点がなく仕様変更できたかを、コードベースで明示する*

*4. 設計の変化によって、どのような仕様変更に耐えうるようになったかをまとめる*

それでは早速始めていきます。

# Part1: ベースとなるシンプルな API を作成する

Part1では、以降のPartの解説のベースとなるAPIを作成します。

作成する際に、

このAPIを、**仕様変更を想定せず、意図的にモノリシックなものとなるように実装を進める**ように意識してみました。

意図的にモノリシックにすることで、CleanArchitecture を適用した際、設計のメリットを可視化しやすくする狙いがあります。

段階的にファイルが責務ごとに分割され、結合が除々に疎になっていく様子を、以降のPartで観察しましょう。


## CleanArchitectureを段階的に適用する最初の成果物

今回は

1. **POSTリクエストを受けて、メモを保存する**

2. **GETリクエストを受けて、保存したメモを参照する**

だけのメモ API を用意します。

## 実装

Webアプリケーションフレームワーク Flask を採用して、シンプルな api を作成します。

#### 1. エンドポイントを用意する

要件を再掲しますが、今回作成する api は、

1. **POSTリクエストを受けて、メモを保存する**
2. **GETリクエストを受けて、保存したメモを参照する**

です。

要件を満たす実装では、`memo_id` をプライマリーキーとして、`memo` を扱うこととします。

まず上記 2 点の処理を実行するエンドポイントを用意します。

---

1. Flaskを用いて、**POSTリクエストを受けて、メモを保存する** ためのエンドポイントを用意します。

    ```python
    from flask import Flask, request
    app = Flask(__name__)
    
    @app.route('/memo/<int:memo_id>', methods=['POST'])
    def post(memo_id: int) -> str:
        # リクエストから値を取得する
        memo: str = request.form["memo"]
        pass
    ```

2. 同様に、**GETリクエストを受けて、保存したメモを参照する** ためのエンドポイントを用意します。
    
    ```python
    @app.route('/memo/<int:memo_id>')
    def get(memo_id: int) -> str:
        pass
    ```

#### 2. DB とメモのやりとりをする部分を用意する

では、このエンドポイントに、メモを保存する DB とのやりとりを記載していきます。
今回は保存する db として、mysql を採用しています。

---

1. まず、`memo_id` で `memo` の有無を確認するための関数を用意します。

    ```python
    from mysql import connector
    
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
    ```
   
2. 次に、**POSTリクエストを受けて、メモを保存する** 処理を、作成したエンドポイントに追記します。

    ```python
    from flask import Flask, request, jsonify
    from mysql import connector
    from werkzeug.exceptions import Conflict
    app = Flask(__name__)
    
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
    
    ```

---

3. 次に、**GETリクエストを受けて、外部のDBに保存したメモを参照する** 処理を実装します。

    ```python
    from werkzeug.exceptions import NotFound
    
    
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
    
    ```

4. 次に、エラーハンドラを設定します。

    ```python
    from http import HTTPStatus
    from flask import make_response
    
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
    ```

---

#### 3. appを起動

最後に、これまでに生成した各routerを付与した、`app` を起動する処理を,ファイル内に記載します。

    ```python
    
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')
    
    ```

#### 4. 最終的なコード

*main.py*

```python
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


```

※ リクエスト単位でconnectionを張るのはあまりイケてないのですが、設計をわかりやすく説明できるよう、敢えてこのような形としています。この点は後ほど、話の展開の中できちんと回収します。


## Part1を終えて

これで、下記 2 点 を実行する API が用意できました。

1. **POSTリクエストを受けて、メモを保存する**
2. **GETリクエストを受けて、保存したメモを参照する**

以降の記事では、各 part ごとに、container環境も含めすべてのコードを下記のリポジトリに格納してるので、
手元で動かしてみたい方は下記を参照してみてください。

> Part1: TODO:

次のPartから、このAPIに対しての仕様変更依頼を仮定し、CleanArchitectureを段階的に適用していきましょう。
