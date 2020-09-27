# Part5: ~番外編~ DTOの活用　

さて、Part4では、Controllersを追加することで、
受け付けるリクエストの形式の変更に対応しやすい設計となりました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。
> Part4 
## 1. 成果物に対して、仕様変更依頼を受ける

ここで、

**「`memo_author` キーを追加して、メモごとにメモの著者を管理したい」**

という仕様変更依頼があった場合について考えてみます。

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

#### 現状の設計で変更を加える場合のコーディング

結論からいうと、

現在の設計では、

APIで扱うキーが 1 つ増えるという変更に対して、

- `flask_controller.py`
- `memo_handle_interactor.py`
- `memo_repository.py`

の 3 つの既存のファイルを変更することで、`memo_author`を追加することができそうです。

---

まず、`flask_controller.py` に、外部から受け取った`request`オブジェクトから、 `memo_author` キーを取得する処理を追記してみましょう。

*interface_adapters/controllers/flask_controller.py*
```python
class FlaskController:
    def save(self, memo_id: int, request) -> str:
        memo = request.json["memo"]
+       memo_author = request.json["memo_author"]
-       return MemoHandleInteractor().save(memo_id, memo)
+       return MemoHandleInteractor().save(memo_id, memo, memo_author)
```

外部から受け取った`memo_author`の取得については問題なさそうです。
また、Part4で導入したcontrollerのおかげで、
`flask_router.py` のことを考えずに、request オブジェクトのParse部分を修正することができました。

---

今回の要件では、最終的に、DB に対して、`memo` と一緒に、 `memo_author` を追加したいです。


なので、`memo_repository.py`で、`memo_author` の値を受け取れるようにしたいのですが、


そう考えると、`flask_controller.py` から `memo_repository.py` までの全ての関数の引数の形式を変更する必要がありそうです。

まず、Controllerで引き出した `memo_author` を、Interactorの引数に追加します。

*interface_adapters/controllers/flask_controller.py*
```python
        ...
-       return MemoHandleInteractor().save(memo_id, memo)
+       return MemoHandleInteractor().save(memo_id, memo, memo_author)
        ...
```

Controllerで引数に設定した `memo_author` を受け取れるよう、Interactorの引数の形式を修正します。
そして、`MemoRepository`のメソッドの引数に、`memo_author`を追加します。
 
*application_business_rules/memo_handle_interactor.py*

```python
class MemoHandleInteractor:
    ...
-   def save(self, memo_id, memo) -> str:
+   def save(self, memo_id, memo, memo_author) -> str:
-       MemoRepository().save(memo_id, memo)
+       MemoRepository().save(memo_id, memo, memo_author)
        return 'saved.'
```

そして、最後に `memo_author`を扱う関数の引数の形式を変更し、
メソッド内部のクエリも、`memo_author`を許容するように変更します。

*enterprise_bussiness_rules/memo_repository.py*

```python
class MemoRepository:

    ...

-   def save(self, memo_id, memo) -> bool:
+   def save(self, memo_id, memo, memo_author) -> bool:
        
        ...
        # memoを保存する
-       query = "INSERT INTO test_table (memo_id, memo) VALUES (%s, %s)"
-       cursor.execute(query, (memo_id, memo))

+       query = "INSERT INTO test_table (memo_id, memo, memo_author) VALUES (%s, %s, %s)"
+       cursor.execute(query, (memo_id, memo, memo_author))

```

#### 現状の設計で変更を加える場合のコーディングの懸念点

上記のように、現在の設計では、

APIで扱うキーが 1 つ増えるという変更に対して、

- `flask_controller.py`
- `memo_handle_interactor.py`
- `memo_repository.py`

`memo_repository.py` へ、新たに追加されたキー`memo_author`をリレーするべく、
Controller以降の全てのレイヤーのメソッドで、引数の形式を変更する必要があります。

今回は、`memo_id`,`memo`,`memo_author`という3つの引数のみでしたが、
実際の開発、例えばマッチングアプリ等だと、ユースケースを処理するために必要な引数は、両手で数えても足りないかもしれません。

ex) ユーザーネーム,ハンドルネーム,年齢,性別,居住地,出身地...

都度変更に対して、引数が宣言されているかどうかを確認しつつ、Controller以降のレイヤー全てのメソッドの引数の形式に対して、変更を行うのはなかなか骨が折れそうです。

懸念点をまとめると、**現在の設計では、レイヤー間の情報の受け渡しが複雑になってしまいそう**です。

## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理

それぞれのレイヤーが、`memo_id` や `memo` といった値を、個別に受け取っているため、
値が追加になった際、以降のレイヤーすべての引数を変更する必要があり、

**レイヤー間の情報の受け渡しが複雑になってしまいそう**です。

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

結論から言えば、各層の情報の受け渡しに、DTO を用いることで、以降これに類する仕様変更をスムーズに行えそうです。

> DTOについて : https://www.deep-rain.com/programming/server-side/267

Part3 では、memo_repository からの response に、DTOとして用意した、`MemoData` を用いることで、
レイヤー間の情報のやりとりをスムーズにしました。

ここでは、各レイヤー間のデータのやりとりに、DTO として `MemoData` を用いると良さそうです。

#### ⅲ. 実際のコーディング

各レイヤーで、`MemoData` を引数とし、最終的に `memo_repository` で `MemoData` を展開して処理を実行します。

```
.
├── application_business_rules
│   └── memo_handle_interactor.py
|
├── enterprise_business_rules
│   ├── __init__.py
│   ├── memo_data.py
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
│   └── controllers
│       ├── __init__.py
│       ├── fastapi_controller.py
│       └── flask_controller.py
|
└── main.py
```

##### Interface Adapters 層

*interface_adapters/controllers/flask_controller.py*

```python
class FlaskController:
    
    ... 

    def save(self, memo_id: int, request: request) -> str:
        memo: str = request.json["memo"]
        memo_data: MemoData = MemoData(memo_id,memo)
        return MemoHandleInteractor().save(memo_data)
    
    ...
```

##### Application Business Ryles 層

*application_business_rules/memo_handle_interactor.py*

```python

class MemoHandleInteractor:
    ...
    def save(self, memo_object : MemoData) -> str:
        MemoRepository().save(memo_object)
        return 'saved.'
    ...
```

##### Enterprise Business Rules 層

*enterprise_bussiness_rules/memo_repository.py*

```python
class MemoRepository:
    def save(self, memo_data : MemoData) -> bool:
        memo_id: int = memo_data.memo_id
        memo: str = memo_data.memo
+       memo_author: str = memo_data.memo_author
        ...
```


*enterprise_bussiness_rules/memo_data.py*
```python
@dataclass
class MemoObject:
    memo_id: int
    memo: str
+   memo_author: str
```

---

DTO を用いない場合、複数のレイヤー間で、複雑な引数のリレーを行わなければなりませんでした。

しかしDTO を用いれば、おおよその application では、
あるキーを追加するという仕様変更に対して、

1. DTO 内に新たに追加したい値を宣言する(MemoDataに対するキーの追加)
2. DTO に新たに追加された値を格納する(Controller層)
3. DTO から新たに追加された値を引き出す(`MemoRepository`)

という最小の変更に抑えることができます。

> DTO を用いていない設計になっていた場合 : https://mokabuu.com/it/java/%E3%80%90java%E3%80%91%E9%A0%BC%E3%82%80%E3%81%8B%E3%82%89dto%E3%82%92%E3%81%97%E3%81%A3%E3%81%8B%E3%82%8A%E3%81%A8%E5%AE%9F%E8%A3%85%E3%81%97%E3%81%A6%E6%AC%B2%E3%81%97%E3%81%84%E3%81%8A%E8%A9%B1

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?

さて、ここでは、DTO を設計に適用しました。

DTOを採用することで、レイヤー間のデータアクセスを円滑にすると同時に、
アプリケーションで扱うデータ構造が変化した際に、各レイヤーへの影響を最小限に抑えられるような設計になりました。