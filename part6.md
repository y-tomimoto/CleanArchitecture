# Part6: Interface Adapters 層: Presenter の登場

前回のPart5では、DTOを活用して、
各レイヤー間の値のやりとりをスムーズにしました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。
> Part5 : 

## 1. 成果物に対して、仕様変更依頼を受ける

ここで、

**「各エンドポイントのレスポンスに、1 行広告をつけられるようにしよう!!」**

という仕様変更依頼を受けたとします。

例えば、現在は、*/memo/123* というエンドポイントに対して、メモを取得するためのGETリクエストを投げたとき、

```
memo : [test]
```

というレスポンスを返していますが、今後は、
```
memo : [test] (ad : 今なら70円引き!!XXXXマート!!)
```

という形式でレスポンスを返してほしいとのことです。

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

#### 現状の設計で変更を加える場合のコーディング

Part3 では、`memo_repository.py` からの response を 汎用的に扱える `MemoData` とすることで、
`memo_handle_interactor.py` で適切なレスポンスの形式に変更していました。

*application_business_rules/memo_handle_interactor.py*

```python
class MemoHandleInteractor:
    ...
    def get(self, memo_id):
        result: MemoData = MemoRepository().get(memo_id)
        return f'memo : [{result.memo}]'
    ...
```

現在の設計であれば、最終的にクライアントに表示したいUIを生成する場合、この`memo_handle_interactor.py`に記載することに良さそうです。

```python
class MemoHandleInteractor:
    ...
   def get(self, memo_id):
        result: MemoData = MemoRepository().get(memo_id)
-       return f'memo : [{result.memo}]'
+       return f'memo : [{result.memo}] (ad : 今なら70円引き!!XXXXマート!!)'
    ...
```

#### 現状の設計で変更を加える場合のコーディングの懸念点

では、このまま運用していたとして、

- 毎月広告メッセージを更新にしよう
- 広告枠を増やしたいので、カンマ区切りで3つの会社の広告を載せよう

などの話を受けたとします。

この類の変更依頼は、本質的には UI に関わるなのにも変更にも関わらず、
Application Business Rules を司る `memo_handle_interactor.py` を変更することになります。

実際の開発で、UI の変更頻度、そして、Application Business Rules の変更頻度はどちらも高いです。

UIに対する変更にも関わらず、`memo_handle_interactor.py` に対して修正を行うことは避けたいです。

また、両方同時に修正が入ってしまうと、`memo_handle_interactor.py` がコンフリクトしてしまうなどありそうです。

## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理

**出力する UI を生成する処理が、Application Business Rules を司る、`memo_handle_interactor.py` 部分に内包されてしまっています。**

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

UI を生成する処理が、Application Business Rules 層 `memo_handle_interactor.py` から切り離せていると良さそうです。

#### ⅲ. 理想の設計を、CleanArchitecture で解釈した場合

最終的な UI を描画する役割として、Interface Adapter 層には、Presenter が存在します。

> TODO: 図を挿入

この層に、UI を生成する処理を切り出します。

#### ⅳ. 実際のコーディング

##### Interface Adapter 層

*interface_adapter/presenters/ad_presenter.py*

```python
from enterprise_business_rules.entity.memo_object import MemoObject


class AdPresenter:
    def __init__(self):
        self.ad_message = "今なら70円引き!!XXXXマート!!"

    def create_view_for_get(self, memo_data: MemoData) -> str:
        return f'memo : [{memo_data.memo}] (ad : {self.ad_message})'

    def create_view_for_save(self) -> str:
        return f'saved. (ad : {self.ad_message})'
    
    def create_view_for_get_by_day(self, memo_data: MemoData) -> str:
        return f'本日のメモは [{memo_data.memo}] です!(ad : {self.ad_message})'

```

##### Application Business Rules 層

*application_business_rules/memo_handle_interactor.py*
```python
from interface_adapters.presenter.ad_presenter import AdPresenter


class MemoHandleInteractor:
    def __init__(self, presenter):
        self.presenter = presenter

    def get(self, memo_id) -> str:
        result: MemoData = MemoRepository().get(memo_id)
        return self.presenter.create_view_for_get(result)

    def save(self, memo_data: MemoData) -> str:
        MemoRepository().save(memo_data)
        return self.presenter.save(create_view_for_save)

    def get_by_day_number(self) -> str:
        ...
        return self.presenter.create_view_for_get_by_day(result)

```

#### ⅳ. Output Boundary の登場

##### 新たにPresentersを生成する際の問題点

さて、ここで

**「今後課金ユーザーだけ広告を表示しないようにしたいと思っているので、その切替ができるようにしてくれ!!」**

と言われたとします。

この場合、広告を付与せずにUIを生成する `NonAdPresenter` のようなものを用意すると良さそうです。

*interface_adapter/presenters/non_ad_presenter.py*

```python
from enterprise_business_rules.dto.input_memo_dto import MemoData


class NonAdPresenter:
    def get(self, memo_data: MemoData):
        return f'memo : [{memo_data.memo}]'

    def save(self):
        return 'saved.'
    
    def create_view_for_get_by_day(self, memo_data: MemoData) -> str:
        return f'本日のメモは [{memo_data.memo}] です!'

```

このPresenterを採用する場合は、`MemoHandleInteractor`のコンストラクタに、`NonAdPresenter` を採用すると良さそうです。

*interface_adapters/controllers/flask_controller.py*

```python
class FlaskController:
    def __init__(self, presenter):
        self.presenter = presenter

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor(self.presenter).get(memo_id)

    def save(self, memo_id: int, request: request) -> str:
        memo: str = request.json["memo"]
        memo_author: str = request.json["memo_author"]
        memo_data: MemoData = MemoData(memo_id, memo, memo_author)

        return MemoHandleInteractor(self.presenter).save(memo_data)

    def get_by_day_number(self) -> str:
        return MemoHandleInteractor(self.presenter).get_by_day_number()
```

*frameworks_and_drivers/web/flask_router.py*
```python
@app.route('/memo/<int:memo_id>')
def get(memo_id):
    return jsonify(
        {
-           "message": FlaskController(AdPresenter()).get(memo_id)
+           "message": FlaskController(NonAdPresenter()).get(memo_id)
        }
    )

```
##### 現状の設計で修正を加える場合の懸念点

しかし、現在の設計だと 2 つの懸念点があります。

1. 新しい Presenter を作成する際、既存の Presenter が持つ method を持つよう実装する必要がある。

現在`MemoHandleInteractor` 内では、下記のように、`AdPresenter` が持つメソッド `create_view_for_*` を引き出しています。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    ...

    def get(self, memo_id):
        ...
        return self.presenter.create_view_for_get(result)

    ...

```

仮に `NonAdPresenter` 内のメソッドが、既存の AdPresenter を踏襲せず、`create_ui_for_*` として実装されていたとしましょう。

この場合、`MemoHandleInteractor` でのメソッド実行に失敗してしまいます。

*interface_adapter/presenters/non_ad_presenter.py*
```python
from enterprise_business_rules.entity.memo_object import MemoObject


class NonAdPresenter:
    def create_ui_for_get(self, memo_object: MemoObject):
        return f'memo : [{memo_object.memo}]'

    def create_ui_for_save(self):
        return 'saved.'

```

このように、`MemoHandleInteractor` が、`AdPresenter` のメソッド呼び出しに依存してしまっているため、
新たな Presenter を生成する際は、既存の `AdPresenter` に依存して(模倣して)生成する必要があります。

今回はエンドポイントが 3 種類しかない簡素な API なので、既存の `AdPresenter` を見ながら、関数名や戻り値と引数を参考にして、新たな Presenter を記載することは簡単です。

しかし、実際の開発において、API は、よりたくさんのエンドポイントを持ちます。

なおかつ、今回のように単純なUIを描画する Presenter ではなく、複雑な UI を描画したり、メソッドごとに引数として与えられるオブジェクトの型が異なったりします。

この中で、`既存の Presenter を模倣して新しいPresenterを作成しなければいけない` という紳士協定を守りつつ実装を進めることは、とてもハードです。

Application の仕様ではなく、UI の変更によって、Application の仕様を管理する memo_handle_interactor を変更するのは避けたいです。

##### 設計上の懸念点を再整理

1. MemoHandleInteractor が、`AdPresenter` のメソッド呼び出しに依存してしまっている

   - そのために、新たな Presenter を生成・切り替えする際、 既存の`AdPresenter` に依存して(模倣して)新たな Presenter を作成する必要があり、変更のハードルが高い。

##### どのような設計なら、懸念点を回避して仕様変更できるか

ここで、CleanArchitecture における、`Output Port` を採用します。
Output Portとは、PresenterのInterfaceの役割を担います。
> Output Port について:  https://medium.com/@manakuro/clean-architecture-with-go-bce409427d31

これだけだとなぜ `Output Port`が、上記の課題を解決するかわかりにくいので、
コードを例示しつつ、`Output Port` を導入する利点を感じていきましょう。

##### 懸念点を回避するための実装

Output Port を作成します。
今回は都度CleanArchitectureの全体図と比較できるよう OutputPort 名で Class を作成していますが、実態は Interface です。

```python
from abc import ABC, abstractmethod

class MemoOutputPort(ABC):
    @abstractmethod
    def create_view_for_get(self, memo_data: MemoData) -> str:
        pass

    @abstractmethod
    def create_view_for_save(self, memo_data: MemoData) -> str:
        pass

    @abstractmethod
    def create_view_for_get_by_day(self, memo_data: MemoData) -> str:
        pass

```

まず、Presenter を作成するときは、この `MemoOutputPort` を継承するようにします。
これにより、Presenter は OutputPort に依存するため、既存のPresenterを考慮せず、新規のPresenterを追加することができます。

```python

class AdPresenter(MemoOutputPort):
    def __init__(self):
        self.ad_message = "今なら70円引き!!XXXXマート!!"

    def create_view_for_get(self, memo_object: MemoObject):
        ...
```

この Interface を実装した Presenter を、`MemoHandleInteractor` のコンストラクタに指定します。

```python


class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort):
        self.presenter = presenter

    def get(self, memo_id):
        ...

```


これにより、紳士協定的に、既存の Presenter を参考にして Presenter を作成せずとも、
Interface を継承することで、型に依存し Presenter を実装することができます。

また、現在は、Controller層のコンストラクタとしてPresenterを受け取り、
内部層でのPresenterの変更を行っていますが、

```python
class FlaskController:
    def __init__(self, presenter: MemoOutputPort):
        self.presenter = presenter

    def get(self, memo_id: int) -> str:
        return MemoHandleInteractor(self.presenter).get(memo_id)
      
    ...
```

各処理ごとに、エンドポイントごとにPresenterを分けたいケースでは、
Controller層のコンストラクタとしてPresenterを受け取らず、内部で宣言するという方法でも良いかと思います。

```python
class FlaskController:
-   def __init__(self, presenter: MemoOutputPort):
-       self.presenter = presenter

   def get(self, memo_id: int) -> str:
-       return MemoHandleInteractor(self.presenter).get(memo_id)
+       return MemoHandleInteractor(AdPresenter()).get(memo_id)
    ...
```

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?

さて、Presenter の実装に加えて、OutputPort の実装も行いました。

これにより、UIを変更する際、既存のWebアプリケーションフレームワークや、ビジネスルールを考慮せず、UIのみ を独立して変更することが可能になりました。

このPresenterの導入により、CleanArchitecture のルール、UI独立が達成されています。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> UI独立。UIは、容易に変更できる。システムの残りの部分を変更する必要はない。たとえば、ウェブUIは、ビジネスルールの変更なしに、コンソールUIと置き換えられる。