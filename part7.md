# Part7 :Frameworks & Drivers 層: DB と Interface Adapters 層: Gateways の登場

さて、Part6では、`Presenter`を用いて、
最終的に出力する形式を、柔軟に変更することができるようになりました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。
> Part6: 

## 1. 成果物に対して、仕様変更依頼を受ける

**「DBは MySQL ではなく PostgreSQL を採用しよう!!」**

というような話があったとします。

現在は、アプリケーションに本来期待する**メモの保存・取得**という処理を、Enterprise Business Rules 層の
`MemoRepository` に配置しています。

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

#### 現状の設計で変更を加える場合のコーディング

現在は、`memo_repository.py` 内で
現在の設計のまま DB を変更するのであれば、下記のようになるでしょう。

```python
# from mysql import connector
import psycopg2
from psycopg2._psycopg import Error, IntegrityError

...

class MemoRepository:

    def exist(self, memo_id: int) -> bool:
        # DBクライアントを作成する
-       conn = connector.connect(**config)
+       conn = psycopg2.connect(host='postgres', dbname='test_database', user='root', password='password', port='5432') # NEW
+       conn.autocommit = True # NEW
        cursor = conn.cursor()

        ...

    def get(self, memo_id: int) -> MemoData:
        ...
        # DBクライアントを作成する
        # conn = connector.connect(**config)
        conn = psycopg2.connect(host='postgres', dbname='test_database', user='root', password='password', port='5432') # NEW
        conn.autocommit = True # NEW
        cursor = conn.cursor()
        ...

    def save(self, memo_data: MemoData) -> bool:
        ...

        # DBクライアントを作成する
-       conn = connector.connect(**config)
+       conn = psycopg2.connect(host='postgres', dbname='test_database', user='root', password='password', port='5432') # NEW
+       conn.autocommit = True
        cursor = conn.cursor()

        ...

```
#### 現状の設計で変更を加える場合のコーディングの懸念点

Part2でも触れましたが、

今回修正を施している`MemoRepository`は、`Mysql` に対してメモの永続化を行うクラスです。

新たに対応するDBとして `PostgreSQL` を追加するにあたり、この `MemoRepository` を修正していますが、
今後、再度`Mysql` に対してメモの永続化を行うかもしれません。

できれば、変更に対して、既存のコードの修正ではなく、コードを追加する形式で対応したいです。

※ オープン/クロースドの原則は、**変更が発生した場合に既存のコードには修正を加えずに、新しくコードを追加する**とする原則です。今回のケースでは、新たにDBを追加するにあたり、既存のコードに対する修正が多く発生しています。
> Open/closed principle：オープン/クロースドの原則: https://medium.com/eureka-engineering/go-open-closed-principle-977f1b5d3db0


## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理
変更に対して、既存のコードの修正ではなく、コードを追加する形式で対応できないため、DBの再利用性が損なわれそう。

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

現在、`MemoRepository`内で、永続化を目的としたDBを宣言しています。

懸念点を回避するべく、内部で宣言する形式ではなく、
この`MemoRepository`のコンストラクタとして、外部に切り出した DB を DI できると良さそうです。

#### ⅲ. 理想の設計を、CleanArchitecture で解釈した場合

Frameworks & Drivers 層: DB に、DBを切り出すと良さそうです。

#### ⅲ. 実際のコーディング

*tree*
```
.
├── application_business_rules
│   ├── __init__.py
│   ├── boundary
│   │   ├── __init__.py
│   │   └── output_port
│   │       ├── __init__.py
│   │       └── memo_output_port.py
│   └── memo_handle_interactor.py
├── enterprise_business_rules
│   ├── __init__.py
│   ├── memo_data.py
│   └── memo_repository.py
├── frameworks_and_drivers
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── mysql.py
│   │   └── postgres.py
│   └── web
│       ├── __init__.py
│       ├── fastapi_router.py
│       └── flask_router.py
├── interface_adapters
│   ├── __init__.py
│   ├── controller
│   │   ├── __init__.py
│   │   └── flask_controller.py
│   └── presenter
│       ├── __init__.py
│       ├── ad_presenter.py
│       └── default_presenter.py
└── main.py


```

##### MemoRepository

まず、コンストラクタとして、DBを受け取り、それを内部で使用するよう実装します。

*enterprise_business_rules/memo_repository.py*

```python
class MemoRepository:
    def __init__(self, memo_repository):
        self.memo_repository = memo_repository

    def exist(self, memo_id: int) -> bool:
        return self.memo_repository.exist(memo_id)

    def get(self, memo_id: int) -> MemoData:
        return self.memo_repository.get(memo_id)

    def save(self, memo_data: MemoData) -> bool:
        return self.memo_repository.save(memo_data)
```

##### Mysql・Postgre

次に、DB自体の処理を、Frameworks & Drivers 層に切り出します。
この際、各メソッド内で都度生成していたconnectionを、コンストラクタとして受け取る形式にします。

*frameworks_drivers/db/mysql.py*
```python
class Mysql:
    def __init__(self, connector):
        self.conn = connector    

    def exist(self, memo_id) -> bool:
        ... 

```

*frameworks_drivers/db/postgres.py*
```python
class PostgreSQL:
    def __init__(self,connector):
        self.conn = connector    

    def exist(self, memo_id) -> bool:
        ...
```

あとは、Part7のPresenterと同様に、Application Business Rules 層と、Interface Adapter層で、
コンストラクタとしてDBを与えると良さそうです。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
        result: MemoObject = MemoRepository(self.repository).get(memo_id)
        return self.presenter.get(result)

```

*interface_adapters/controllers/flask_controller.py*
```python
class FlaskController:
    def __init__(self, presenter: MemoOutputPort, repository):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor(self.presenter,self.repository).get(memo_id)
```


ここで *enterprise_business_rules/memo_repository.py*と、memo_handle_interactor.py を比較してみます。

DBとの処理を、*enterprise_business_rules/memo_repository.py*からDBに移行したので、
*enterprise_business_rules/memo_repository.py*内では、コンストラクタとして受け取った `memo_repository` を実行しているのみになります。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
        result: MemoData = MemoRepository(self.repository).get(memo_id)
        return self.presenter.create_view_for_get(result)

    def save(self, memo_data: MemoData):
        MemoRepository(self.repository).save(memo_data)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
            result: MemoData = MemoRepository(self.repository).get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        return self.presenter.create_view_for_get_by_day(result)
```

*enterprise_business_rules/memo_repository.py*
```python
class MemoRepository:
    def __init__(self, memo_repository):
        self.memo_repository = memo_repository

    def exist(self, memo_id: int) -> bool:
        return self.memo_repository.exist(memo_id)

    def get(self, memo_id: int) -> MemoData:
        return self.memo_repository.get(memo_id)

    def save(self, memo_data: MemoData) -> bool:
        return self.memo_repository.save(memo_data)
```

DBとの本来の処理を、DBレイヤーに移行したので、このMemoRepositoryクラスを経由せず、
*application_business_rules/memo_handle_interactor.py* で直接実行したいと思います。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
-       result: MemoData = MemoRepository(self.repository).get(memo_id)
+       result: MemoData = self.repository.get(memo_id)
        return self.presenter.create_view_for_get(result)

    def save(self, memo_data: MemoData):
-       MemoRepository(self.repository).save(memo_data)
+       self.repository.save(memo_data)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
-           result: MemoData = MemoRepository(self.repository).get(day_number)
+           result: MemoData = self.repository.get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        return self.presenter.create_view_for_get_by_day(result)
```


#### ⅴ. Gatewaysの登場

さて、ここで、先程のpart6のPresenterのケースを思い出してください。

外部からPresenterをDIする際、Interfaceが用意されていない場合、
新規にPresenterを追加する際、既存のPresenterに暗黙的に依存した実装を行わなければならないという課題がありました。

part8でも同じように、Interfaceがなければ、各DBの実装をすすめる際、既存のDBのコードに依存しつつ実装を進めなければなりません。

そこで、part8もpart7と同様に、DBのInterfaceを用意することで、上記の問題が解決できそうです。

DBにおけるInterfaceは、CleanArchitectureでは `Gateways` と呼びます。

*interface_adapters/gateways/memo_repository_gateway.py*

```python

class MemoRepositoryGateway(metaclass=ABCMeta):
    @abstractmethod
    def get(self, memo_id: str) -> MemoData:
        pass

    @abstractmethod
    def save(self, memo_data: MemoData) -> MemoData:
        pass

    @abstractmethod
    def exist(self, memo_id: str) -> bool:
        pass

```


---

`MemoHandleInteractor`では、`Gateway`を継承したClassを、コンストラクタとして受け取るように実装します。

```python
class MemoHandleInteractor:
-   def __init__(self, presenter: MemoOutputPort, repository):
+   def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository
        ...
```


---

各DB(Mysql・PostgreSQL)では、このGatewayを実装してClassを生成します。

*frameworks_drivers/db/mysql.py*
```python
- class Mysql:
+ class Mysql(MemoRepositoryGateway):
        ... 
```

*frameworks_drivers/db/postgresql.py*
```python
- class PostgreSQL:
+ class PostgreSQL(MemoRepositoryGateway):
        ...
```

そして、`Controller` でも同様に、DBをコンストラクタとして受け取る際に、
`MemoRepositoryGateway` を指定します。

*interface_adapters/controllers/flask_controller.py*
```python
class FlaskController:
-   def __init__(self, presenter: MemoOutputPort):
+   def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
+       self.repository = repository

    def get(self, memo_id: int) -> str:
-       return MemoHandleInteractor(self.presenter).get(memo_id)
+       return MemoHandleInteractor(self.presenter,self.repository).get(memo_id)

        
``` 

最終的なディレクトリ構成は下記のようになります。

*tree*
```
.
├── application_business_rules
│   ├── __init__.py
│   ├── boundary
│   │   ├── __init__.py
│   │   └── output_port
│   │       ├── __init__.py
│   │       └── memo_output_port.py
│   └── memo_handle_interactor.py
├── enterprise_business_rules
│   ├── __init__.py
│   └── memo_data.py
├── frameworks_and_drivers
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── mysql.py
│   │   └── postgres.py
│   └── web
│       ├── __init__.py
│       ├── fastapi_router.py
│       └── flask_router.py
├── interface_adapters
│   ├── __init__.py
│   ├── controller
│   │   ├── __init__.py
│   │   └── flask_controller.py
│   ├── gataways
│   │   ├── __init__.py
│   │   └── memo_repository_gateway.py
│   └── presenter
│       ├── __init__.py
│       ├── ad_presenter.py
│       └── default_presenter.py
└── main.py
```

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?
さて、今回の章では、DBレイヤーにDBを実装し、Gatawaysを採用しました、

これにより、DBの変更を行う際、各レイヤーを考慮せずに、DBを切り替えることのできる設計となっています。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> データベース独立。OracleあるいはSQL Serverを、Mongo, BigTable, CoucheDBあるいは他のものと交換することができる。ビジネスルールは、データベースに拘束されない。
