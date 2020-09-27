# Part2: Frameworks & Drivers 層: Webの登場

前回のPart1では、なるべくモノリシックに、

1. **POSTリクエストを受けて、メモを保存する**

2. **GETリクエストを受けて、保存したメモを参照する**

だけのメモ API を用意しました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。

> Part1 : 

## 1. 成果物に対して、仕様変更依頼を受ける

Part1 で作成した 『Flaskフレームワークを用いて作成したAPI』 に対して、とある仕様変更依頼を受けました。

**「webアプリケーションフレームワークに Flask ではなく FastAPI を採用しよう。」**

Part1では、この仕様変更依頼を想定して、仕様変更に強い設計を考えてみましょう。

---

フレームワークを交換したいケースに遭遇したことはあまりありませんが、導入として分かりやすい事例かと思い、採用してみました。

余談として、筆者の直近の体験になりますが、市況の変化により、急遽とあるWebアプリケーションのResponse Headerに、
特定のHeaderを付与したいという状況がありました。

しかし、そのHeader属性は近年追加されたものであったため、当時採用していたWebアプリケーションフレームワークが、
そのHeader属性をサポートしておらず、Webアプリケーションフレームワーク自体の変更を迫られたというケースはありました。
(結局カスタムヘッダーに、Headerを生で書いて対応し、事なきを得ましたが、、、) 

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

さて、話を戻します。

現在は、`main.py` 内に、下記の処理がまとめて記載されています。

1. フレームワークによりリクエストを受け付ける
2. アプリケーションに本来期待する処理を実行する（メモの取得・保存）

> main.py : TODO urlを記載する

#### 現状の設計で変更を加える場合のコーディング

現在の設計で、採用するフレームワークを変更するとなると、どのような作業が発生するでしょうか?

フレームワークをFlaskからFastAPIに変更しようとした場合、
既存の `main.py` に下記のような修正を加えることになるでしょう。

1. フレームワークによって構成されたルーターを書き換える
2. レスポンスの形式を書き変える
3. エラーハンドラを書き換える
4. app の起動方法を書き変える

現在の設計のままで、既存の `main.py` に実際の修正を加えると、下記のようになるかと思います。

##### main.py

```python
from http import HTTPStatus
- from flask import Flask, request, jsonify, make_response
+ from fastapi import FastAPI, Form, Response
+ import uvicorn
from mysql import connector

- app = Flask(__name__) 
+ app = FastAPI()

# DB接続用の設定
config = {
    ...
}

def exist(memo_id: int) -> bool:
    ...


- @app.route('/memo/<int:memo_id>')
+ @app.get('/memo/{memo_id}') 
def get(memo_id: int) -> str:

    ...

    
-   return jsonify(
-       {
-           "message": f'memo : [{result[1]}]'
-       }
-   )

+   return JSONResponse(
+       content={"message": f'memo : [{result[1]}]'
+   )


- @app.route('/memo/<int:memo_id>', methods=['POST'])
+ @app.post('/memo/{memo_id}')
- def post(memo_id: int) -> str:
+ async def post(memo_id: int, memo: str = Form(...)) -> str:


    ...

    
-   return jsonify(
-       {
-            "message": "saved."
-       }
-   )

+   return JSONResponse(
+      content={"message": "saved."}
+   )

- @app.errorhandler(NotFound)
- def handle_404(err):
-     json = jsonify(
-         {
-             "message": err.description
-         }
-     )
-     return make_response(json, HTTPStatus.NOT_FOUND)


+ @app.exception_handler(NotFound)
+ async def handle_404(request: Request, exc: NotFound):
+   return JSONResponse(
+       status_code=HTTPStatus.NOT_FOUND,
+       content={"message": exc.description},
+   )

- @app.errorhandler(Conflict)
- def handle_409(err):
-     json = jsonify(
-         {
-             "message": err.description
-         }
-     )
-     return make_response(json, HTTPStatus.CONFLICT)


+ @app.exception_handler(Conflict)
+ async def handle_409(request: Request, exc: Conflict):
+   return JSONResponse(
+       status_code=HTTPStatus.CONFLICT,
+       content={"message": exc.description},
+   )



if __name__ == '__main__':
-   app.run(debug=True, host='0.0.0.0') # DELETE
+   uvicorn.run(app=fastapi_app, host="0.0.0.0", port=5000) # NEW

```

このように力技で仕様変更することは可能ではありますが、いくつか懸念点があります。

#### 現状の設計で変更を加える場合のコーディングの懸念点

この修正では、`main.py` 内の、フレームワークに関するコード を修正しています。

しかし、 `main.py` 内には、フレームワークに関するコードのみならず、アプリケーションに本来期待する、**メモを取得・保存する処理** も記載されています。

※ 複数の役割を一同に持つ `main.py` は`Single Responsibility Principle：単一責任の原則`を満たしていないといえます。
> Single Responsibility Principle：単一責任の原則: https://note.com/erukiti/n/n67b323d1f7c5

この際、**アプリケーションに本来期待する「メモを取得・保存する処理」に対して、誤って不必要な変更を加えてしまう** かもしれません。

既に動作しているコードに対して、誤って不具合を引き起こすのではないか? と考えながら、修正を施すという状況は、なるべく避けたいです。

今回の例では、エンドポイントは 2 つのみですが、これが大規模なサービスで、複数のエンドポイントがある場合、この懸念はより大きなものとなるでしょう。

※ これは、SOLID 原則のうち、`Open/closed principle：オープン/クロースドの原則` に反しているもと言えます。オープン/クロースドの原則は、**変更が発生した場合に既存のコードには修正を加えずに、新しくコードを追加する**とする原則です。今回のケースでは、新たにフレームワークを追加するにあたり、既存のコードに対する修正が多く発生しています。
> Open/closed principle：オープン/クロースドの原則: https://medium.com/eureka-engineering/go-open-closed-principle-977f1b5d3db0

## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理

懸念点 : **正常に動作している既存のコードに、不必要な変更を加えてしまう可能性がある** 

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

今回の懸念点は、`main.py` 内に、フレームワークのみならず、アプリケーションに本来期待する **メモを取得・保存する処理**もまとめられていることに起因しています。

そのため、今回の懸念点は、`main.py` を、

**フレームワーク** と、**アプリケーションに本来期待する処理** に分割すると解消されそうです。

コードを役割ごとに分割した設計になっていれば、修正の影響範囲を、その役割の中だけに留めることができそうです。

#### ⅲ. 理想の設計を、CleanArchitecture で解釈した場合

`main.py` には、

1. flask フレームワークでリクエストを受け取る
2. メモを保存する or メモを取得する

という 2 つの処理があります。

CleanArchitecture よりの言葉で、上記を言い換えると、

1. Web アプリケーションフレームワーク
2. アプリケーションに本来期待する機能

です。

CleanArchitecture で解釈するにあたり、下記の図では、

1. `1` について、Web (Frameworks & Drivers 層の一部)と表せそうです。

2. `2`については、アプリケーションに本来期待する機能ということなので、Application Business Rules 層か、Enterprise Business Rules 層のいづれかに該当しそうですが、ここでは一旦 `メモを保存する or メモを取得する` という機能を形容して、MemoHandler として扱いましょう。

と表わせそうです。

> TODO : 図を挿入

では、`main.py` を Frameworks & Drivers 層: Web と MemoHandler に分割してみましょう。

#### ⅳ. 実際のコーディング

`main.py` からは、Frameworks & Drivers 層: Web　の router を呼び出し、
各 router から、 `memo_handler.py` を呼び出すような設計にします。

この設計にすることで、フレームワークを変更する場合には、`main.py` で呼び出すフレームワークを変更するのみで、
既存の処理である `memo_handler.py` 自体に手を加えないので、誤って既存の処理が変更されることはありません。

*ツリー図*

```
.
├── memo_handler.py 
└── frameworks_and_drivers
    └── web
        ├── fastapi_router.py
        └── flask_router.py

```

##### Frameworks & Drivers 層

*frameworks_and_drivers/web/fastapi_router.py*

```python
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from werkzeug.exceptions import Conflict, NotFound
from memo_handler import MemoHandler
from http import HTTPStatus

app = FastAPI()


@app.get('/memo/{memo_id}')
def get(memo_id: int) -> str:
    return JSONResponse(
        content={"message": MemoHandler().get(memo_id)}
    )


@app.post('/memo/{memo_id}')
async def post(memo_id: int, memo: str = Form(...)) -> str:
    return JSONResponse(
        content={"message": MemoHandler().save(memo_id, memo)}
    )


@app.exception_handler(NotFound)
async def handle_404(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"message": exc.description},
    )


@app.exception_handler(Conflict)
async def handle_409(request: Request, exc: Conflict):
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content={"message": exc.description},
    )


```

*frameworks_and_drivers/web/flask_router.py*

```python

from flask import Flask, request , jsonify , make_response
from werkzeug.exceptions import Conflict,NotFound
from http import HTTPStatus
from memo_handler import MemoHandler
app = Flask(__name__)


@app.route('/memo/<int:memo_id>')
def get(memo_id: int) -> str:
    return jsonify(
        {
            "message": MemoHandler().get(memo_id)
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    memo: str = request.form["memo"]
    return jsonify(
        {
            "message": MemoHandler().save(memo_id, memo)
        }
    )


@app.errorhandler(NotFound)
def handle_404(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json,HTTPStatus.NOT_FOUND)


@app.errorhandler(Conflict)
def handle_409(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json, HTTPStatus.CONFLICT)


```

##### MemoHandler

*memo_handler.py*

```python
from mysql import connector
from werkzeug.exceptions import Conflict, NotFound

# sqlクライアント用のconfig
config = {
    'user': 'root',
    'password': 'password',
    'host': 'mysql',
    'database': 'test_database',
    'autocommit': True
}


class MemoHandler:

    def exist(self, memo_id: int):
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

    def get(self, memo_id: int):

        # 指定されたidがあるかどうか確認する
        is_exist: bool = self.exist(memo_id)

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

        return f'memo : [{result[1]}]'

    def save(self, memo_id: int, memo: str):

        # 指定されたidがあるかどうか確認する
        is_exist: bool = self.exist(memo_id)

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

        return "saved."



```

##### main.py

`main.py` 上で採用するフレームワークを切り替えます。

*main.py*

```python

import uvicorn
from frameworks_and_drivers.flask_router import app as fastapi_app
from frameworks_and_drivers.flask_router import app as flask_app

---

# フレームワークとしてflaskを採用する場合
flask_app.run(debug=True, host='0.0.0.0')

---

# フレームワークとしてfast_apiを採用する場合
uvicorn.run(app=fastapi_app, host="0.0.0.0",port=5000)

```

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?

各フレームワークを、Frameworks & Drivers 層: Web に切り出し、本来アプリケーションに期待する処理を `MemoHandler` に切り出したことで、
採用したい router を、`main.py` で呼び出すだけで、**アプリケーションに本来期待する処理である、`memo_handler.py` に手を入れることなく、フレームワークを柔軟に変更** することができました。

この設計では、CleanArchitecture のルールの 1 つ、**フレームワーク独立** が実現されています。

> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> フレームワーク独立: アーキテクチャは、機能満載のソフトウェアのライブラリが手に入ることには依存しない。これは、そういったフレームワークを道具として使うことを可能にし、システムをフレームワークの限定された制約に押し込めなければならないようなことにはさせない。
