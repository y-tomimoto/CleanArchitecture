# Part4: Interface Adapters 層: Controllers の登場

さて、前回のPart3では、main.py は、

`MemoHandler`クラスを、

- Application Business Rules
- Enterprise Business Rules

に分割しました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。
> Part3: 

## 1. 成果物に対して、仕様変更依頼を受ける

ここで、

**「JSON 形式で POST リクエストを受け付けるように仕様を変更してくれ!!」**

という依頼があったとします。

なお、現在は下記のような form 形式での post リクエストしか受け付けていません。

```shell script
curl --location --request POST 'localhost:5000/memo/1' \
--form 'memo=momomo'
```

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

#### 現状の設計で変更を加える場合のコーディング

現在の設計のまま、jsonを受け付けることができるよう修正するのであれば、下記のようになるでしょう。

```python
@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    #   memo = request.form["memo"]
    memo: str = request.json["memo"] # NEW

    return jsonify(
        {
            "message": MemoHandleInteractor().save(memo_id, memo)
        }
    )


```

#### 現状の設計で変更を加える場合のコーディングの懸念点

まず第一に、既存のコードを修正する形式での変更になってしまいます。

仕様変更の際、routerのコードも誤って変更しかねないのは、懸念点として挙げられます。

また、リクエスト body の形式だけではなく、今後 json のキーの値が変更・追加になるかもしれません。

例えば

- `memo` を `memo_text` 名でフロントから投げたい
- `memo` 以外に、`memo_author` キーを追加する

等です。

リクエスト body 形式の変更(Form・json 等)については、変更の頻度は少ないかもしれませんが、
上記のようなキーの変更や、キーの追加は、サービスを運用していく上では往々にしてあると思います。


```python


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id):
    # memo = request.form["memo"]
    # memo = request.json["memo"]
    memo = request.json["memo_text"] # NEW
    memo_author = request.json["memo_author"] # NEW
    ...

```

これらの仕様変更があるたびに、router 内の、

`受け取ったリクエストから、キーによって値を抽出する`

部分の修正が必要になります。

実際の開発では、

- フレームワークの仕様変更の頻度
- リクエスト body の形式、及びキー名の形式変更の頻度

は異なり、リクエスト body の形式、及びキー名の形式変更の頻度のたびに、
フレームワークを管理する `router.py` ファイルを変更するのは避けたいです。

## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理

今回、Flask フレームワークでは、`request`オブジェクト内から値を引き出すようになっています。

```python
@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    # memo = request.form["memo"]
    memo: str = request.json["memo"] # NEW
```

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

現在、`flask_router.py`内で、`request`オブジェクト内から引き出した値を、`MemoHandleInteractor` 内の関数に、引数として渡していますが、

`flask_router.py` から、

**`request`オブジェクト内から、`MemoHandleInteractor` 内の関数の引数として適した形式に加工する**

部分を、フレームワーク部分を担うファイルから切り出せると良さそうです。


#### ⅲ. 理想の設計を、CleanArchitecture で解釈した場合

外部から受け取った値を、実際の処理に適した形式に変換するという責務を担う役割として、CleanArchitecture 内では、Interface Adapters 層の、Controllers が存在します。

> Interface Adapters層について : https://blog.tai2.net/the_clean_architecture.html 
>> このレイヤーのソフトウェアは、アダプターの集合だ。これは、ユースケースとエンティティにもっとも便利な形式から、データベースやウェブのような外部の機能にもっとも便利な形式に、データを変換する。(省略...)
 

今回は、

フレームワークから受け取った値(外部の機能にもっとも便利な形式)を、

MemoHandleInteractor.save（ユースケースとエンティティ）に渡すため、

MemoHandleInteractor.save の引数に適した形(ユースケースとエンティティに最も便利な形)に変換する
 
ためのController を用意します。

Controller の 抽象的なイメージ については、下記記事内の画像がとてもわかり易かったです。

> TODO : ゲームの Controller の図を記載すること


#### ⅳ. 実際のコーディング

```
.
├── application_business_rules
│   └── memo_handle_interactor.py
|
├── enterprise_business_rules
│   ├── __init__.py
│   ├── entity
│   │   ├── __init__.py
│   │   └── memo_object.py
│   └── memo_repository.py
|
├── frameworks_and_drivers
│   ├── __init__.py
│   └── web
│       ├── __init__.py
│       ├── fastapi_router.py
│       └── flask_router.py
|
├── interface_adapters
│   ├── __init__.py
│   ├── __pycache__
│   └── controllers
│       ├── __init__.py
│       ├── fastapi_controller.py
│       └── flask_controller.py
|
└── main.py


```



##### Interface adapters 層 : controller

新たに `FlaskController` という、`request` から値を取得し、`MemoHandleInteractor` の引数に合う形式で戻り値を返す関数を持つ class を用意します。

これにより、外部から受け取った値を、実際の処理に適した値に加工する場合は、この Controller のみを変更すれば大丈夫です。

*interface_adapters/controllers/flask_controller.py*

```python
class FlaskController:
    def save(self, memo_id, request) -> str:
        # memo = request.form["memo"]
        memo: str = request.json["memo"]
        return MemoHandleInteractor().save(memo_id, memo)

```



##### Framework & driver 層

`flask_router.py` からは、この Controller 呼び出します。
これにより、仮に外部からの値の受け取り方が変更になっても、フレームワークを管理するrouterを変更せずに済みます。


*frameworks_and_drivers/web/flask_router.py*

```python
@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    return jsonify(
        {
            "message": FlaskController().save(memo_id, request)
        }
    )

```

Part4の全てのコードは下記です。
> TODO : URLを配置

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?

さて、今回は、Interface Adapters 層の Controller を活用することによって、
更新頻度の高い、『外部からのリクエスト形式』を、実際の処理に適した形式に変更するという部分を、
フレームワークから切り出すことができました。

これにより、アプリケーションで受け入れることのできるリクエストの形式を変更する際、
既存のWebアプリケーションフレームワークや、ビジネスルールを考慮せずに、コードの修正を行うことができるようになりました。