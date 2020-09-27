# Part8: Enterprise Business Rules 層: Entity & Value Object の採用
 
さて、Part7では、DBレイヤーを用いて、
採用するDBを柔軟に変更することができました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。
> Part7: 

## 1. 成果物に対して、仕様変更依頼を受ける

さて、ここで、

**「利用しているユーザーが、どのブラウザorデバイスからメモを参照しているか知りたいので、メモを保存する際は、メモを登録した人のUserAgentも一緒にしてくれ。」**

という仕様変更依頼を受け取ったとします。

前提として、このメモAPIでは、ユーザーごとにエンドポイントを割り振らず、グローバルに公開しているとします。
これにより、誰かに自分のメモを見てもらったり、自分も誰かのメモを見ることができるような状態が達成されています。

ex)
1. `memo_author` である田中 が、`memo`: 『今日は暑い。』を `memo_id` : 『1』で登録する
2. 第三者が `/memo/1` へのGETリクエストを送信すると、田中さんが登録したメモが見える。 

このとき、**ユーザーのメモと共に保存されているUserAgentを、第三者に公開することがないよう、気をつけて実装する**必要がありそうです。

## 2. 現在の設計のままで仕様変更依頼に対応する際の懸念点

#### 現状の設計で変更を加える場合のコーディング

##### 1. UserAgentを扱えるように修正する

1. まず、`flask_controller.py` で、`request`オブジェクトからUserAgentを取得し、そのUserAgentを、`MemoData` オブジェクトで扱えるように修正しましょう。

*interface_adapters/controllers/flask_controller.py*

```python
class FlaskController:
    ...
    def save(self, memo_id: int, request: request) -> str:
        memo: str = request.json["memo"]
        memo_author: str = request.json["memo_author"]
+       memo_user_agent: str = request.headers.get('User-Agent')
-       memo_data: MemoData = MemoData(memo_id, memo, memo_author)
+       memo_data: MemoData = MemoData(memo_id, memo, memo_author, memo_user_agent)

```

*enterprise_business_rules/memo_data.py*

```python
@dataclass
class MemoData:
    memo_id: int
    memo: str
    memo_author: str
+   memo_user_agent: str 

```

この2点の修正だけで、DB層で `memo_user_agent` を扱うことができます。

*frameworks_and_drivers/db/mysql.py*

```python
class Mysql(MemoRepositoryGateway):

    ...

    def save(self, memo_data: MemoData) -> bool:
    memo_id: int = memo_data.memo_id
    memo: str = memo_data.memo
    memo_author = memo_data.memo_author
+   memo_user_agent = memo_data.memo_user_agent
    
    ...

-   query = "INSERT INTO test_table (memo_id, memo, memo_author) VALUES (%s, %s, %s)"
+   query = "INSERT INTO test_table (memo_id, memo, memo_author, memo_user_agent) VALUES (%s, %s, %s, %s)"
-   cursor.execute(query, (memo_id, memo, memo_author))
+   cursor.execute(query, (memo_id, memo, memo_author, memo_user_agent))

    
```

これでUserAgentを扱えるようになりました。

##### 2. UserAgentを外部に公開しないように設定する。

では、次にこのUserAgentを外部に公開しないように設定しましょう。

このAPIは、GETリクエストを受けた際に、DB内に保存されているメモを、MemoDataオブジェクトに詰めて、レスポンスとして返します。

*frameworks_and_drivers/db/mysql.py*

```python
class Mysql(MemoRepositoryGateway):
    def get(self, memo_id: int) -> MemoData:

        ...

-       return MemoData(memo_id=memo_id, memo=result[1], memo_author=result[2])
+       return MemoData(memo_id=memo_id, memo=result[1], memo_author=result[2], memo_author=result[3])
```

現在`MemoData` オブジェクトは、`memo_user_agent` プロパティを持っていますが、

ここでUserAgentを代入せずに、`MemoData` オブジェクトを戻り値として返せばひとまず要件は達成できそうです。

*frameworks_and_drivers/db/mysql.py*

```python
class Mysql(MemoRepositoryGateway):
    def get(self, memo_id: int) -> MemoData:

        ...

-       return MemoData(memo_id=memo_id, memo=result[1], memo_author=result[2])
+       return MemoData(memo_id=memo_id, memo=result[1], memo_author=result[2], memo_user_agent="この値は公開されていません。")
```

#### 現状の設計で変更を加える場合のコーディングの懸念点

今回は、UserAgentでしたので、秘匿したい情報をこのような手法で外部に流さないという方法が取れると思います。

しかし、これが**ユーザーのメールアドレス**や**電話番号**だとしたらどうでしょう??
これらの情報もUserAgentと同様に秘匿したい情報ですが、これらの情報は 各Business Rules で必要になることもあるはずです。

仮に、**メールで、ユーザーをプラチナ会員へ招待する**ケースを考えてみましょう。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
        ...
    def invite_platinum_member(self, memo_id: int) -> str:
        result: MemoData = MemoRepository(self.repository).get(memo_id)
        mail = result.memo_author_mail_address
        platinum.invite_by_mail(mail)
        ...
```

このケースのように、秘匿性の高い情報を活用する Business Rules もあるため、

*frameworks_and_drivers/db/mysql.py* が、秘匿性の高い情報を返したり返さなかったりすると、汎用的にDB層を利用することができません。

---

ここで、Presenter層を活用する案が頭をよぎります。

このコード上で、最終的にUserへUIを返すのはPresenter層です。
汎用的にDB層を利用するために、データを全て返し、Presenter層で、秘匿性の高い情報を誤って引き出さなければ良いのでは??

今回のケースでいうと、第三者へUserAgentを公開しないことを考え、このPresenter層で、`memo_data.memo_user_agent` を呼び出さなければ良いではないか!という話になりそうです。

*interface_adapters/presenters/ad_presenter.py*

```python

# memo_data内のmemo_data.memo_user_agentを呼び出さなければ良さそう?

class AdPresenter(MemoOutputPort):
    def __init__(self):
        self.ad_message = "今なら70円引き!!XXXXマート!!"

    def create_view_for_get(self, memo_data: MemoData):
        return f'memo : [{memo_data.memo}] (ad : {self.ad_message})'

    def create_view_for_save(self):
        return f'saved. (ad : {self.ad_message})'

    def create_view_for_get_by_day(self, memo_data: MemoData):
        return f'本日のメモは [{memo_data.memo}] です!(ad : {self.ad_message})'
```

今回のように、Presenterを活用するケースはこれで良いかもしれません。
ただ、`memo_user_agent` が引き出せるような状態での実装では、誤ってこの秘匿した情報を引き出してしまうかもしれません。

また、今後Presenterを適用せず、この`MemoData`オブジェクトを直接レスポンスとして返し、フロントでこのObjectを加工するというケースもあるかもしれません

このように考えると、そもそものレスポンスオブジェクトである、**`MemoData` 自体から、秘匿性の高いプロパティである`memo_user_agent`を引き出せるような設計にはしないほうが良さそう**です。

## 3. 依頼に対して、どのような設計だったら、スムーズに仕様変更できたかを、CleanArchitecture ベースで考えてみる

#### i. 設計上の懸念点を再整理
**DB層で、秘匿性の高い情報を返さない場合、各Business Rules層で、汎用的にDBを活用できない。**

#### ⅱ. どのような設計になっていれば、懸念点を回避して仕様変更できたか

なるべく、DB内の全ての情報を返し、各Business Rules層で、秘匿性の高い情報を隠蔽するためのDTOを採用すると良さそうです。
また、DB内の全ての情報を返すべく、DB層では、DTOではなく、**DB内のデータ構造を持つオブジェクト**を採用できると良さそうです。

#### ⅲ. 理想の設計を、CleanArchitecture で解釈した場合

**DB内のデータ構造を持つオブジェクト**として、既存のDTOではなく、DDDにおけるEntityを採用すると良さそうです。

> Entity : https://qiita.com/takasek/items/70ab5a61756ee620aee6
>>  Entityとは「永続化可能なJavaオブジェクト」をさします。具体的にはRDBにある表に相当するオブジェクトだと思ってください。データベースの表（テーブル）に列（カラム）があるように、Entityには変数（フィールド）があります。またそれらのフィールドを操作するためのアクセッサー･メソッド（getter/setter）があります。Entityをインスタンス化するということは、データベースの行に相当するレコードをEntityのフィールドに関連付けることです。

また、

1. 入力されたデータを受け取るDTO
2. 秘匿性の高い情報を隠蔽するためのDTOと、



を用意し、

1. 秘匿性の高い情報を各レイヤー間で扱えるようにし、
2. Presenter層に秘匿性の高い情報を流出させない

ようにします。

#### ⅳ. 実際のコーディング

##### DTO
まず、


1. 入力されたデータを受け取るDTO
2. 秘匿性の高い情報を隠蔽するためのDTOと、


を用意します。

『入力されたデータを受け取るDTO』は、`MemoData` Classの命名を変更したものです。
*enterprise_business_rules/dto/input_memo_dto.py*
```python
from dataclasses import dataclass


@dataclass
class InputMemoDTO:
    memo_id: int
    memo: str
    memo_author: str
    memo_user_agent: str
```

次に、『秘匿性の高い情報を隠蔽するためのDTO』です。
このClassは、Presenter層に秘匿性の高い情報を流出させないために用います。

Application層で、リポジトリのResponseとして得たEntityから、
外部に公開しても良いプロパティのみを抽出し、Presenter層へ返します。

今回は、`memo_user_agent` を非公開としたいので、このプロパティを持たないデータクラスとなっています。

*enterprise_business_rules/dto/output_memo_dto.py*
```python
from dataclasses import dataclass


@dataclass
class OutputMemoDTO:
    memo_id: int
    memo: str
    memo_author: str
```

##### Entity

次にEntityを追加します。

*enterprise_business_rules/entity/memo.py*

```python
class Memo(object):

    def __init__(self, memo_id, memo, memo_author, memo_user_agent):
        assert isinstance(memo_id, int)
        assert isinstance(memo, str)
        assert isinstance(memo_author, str)
        assert isinstance(memo_user_agent, str)
        self.__memo_id = memo_id
        self.__memo = memo
        self.__memo_author = memo_author
        self.__memo_user_agent = memo_user_agent

    @property
    def memo_id(self):
        return self.__memo_id

    @property
    def memo(self):
        return self.__memo

    @property
    def memo_author(self):
        return self.__memo_author

    @property
    def memo_user_agent(self):
        return self.__memo_user_agent

```

このEntityを、実際のDBとのやりとりで採用します。
`@dataclass` を用いていないのは、Entityを単なるデータ構造として扱わず、
DTOよりも、厳格に各プロパティの再代入を不可能としたオブジェクトとしたいためです。

---

このとき、`InputMemoDTO` と、`Entity` の役割が同じなので、CreateMemoDTOを、Entityと同様に採用してはいいのでは??

と感じるかと思います。

個人的には、EntityとDTOを別で採用したほうが良いと思っています。

それは、**外部から受け取るプロパティと、DBとのやりとりで使用したいプロパティは、必ずしも一致しない**からです。

今回は、下記のpathを用意して、メモのプライマリーキーを `memo_id` としています。

*/memo/123* : `memo_id` を123として管理しており、123で登録したメモを取得できる。

では、下記のようなpathを用意します。

*/memo* : path上にプライマリーキーを表出させず、このエンドポイントにリクエストを送った場合、UUIDを内部で生成し、それをプライマリーキーとする

例) 
1. */memo* にPOSTを投げてメモを登録する
2. レスポンスとしてUUIDを得る
3. そのUUIDで、メモを引き出すことができる。: */memo/{UUID}*

この場合、`InputMemoDTO` とEntity `Memo` が持つプロパティは異なりそうです。

*enterprise_business_rules/dto/input_memo_dto.py*
```python
from dataclasses import dataclass


@dataclass
class InputMemoDTO:
    memo: str
    memo_author: str
    memo_user_agent: str
```

*enterprise_business_rules/entity/memo.py*
```python
class Memo(object):

    def __init__(self, primary_key, memo, memo_author, memo_user_agent):
        assert isinstance(primary_key, UUID)
        ...
```

恐らく、いづれか層で、UUIDを生成し、そのUUIDと`InputMemoDTO`のプロパティを用いて、`Memo` を生成することになると思います。
このように、**外部から受け取るプロパティと、DBとのやりとりで使用したいプロパティは、必ずしも一致しない**ため、個人的にはDTOとEntityは独立しているほうが、都合が良いかと思います。

##### Application Business Rules 層

では、先程追加したDTOとEntityを、実際に採用してみます。

やっていることは、

- 外部から `InputMemoDTO` を受け取り、`Memo` Entityに詰めてDBに渡す
- DBから `Memo` Entityを受け取り、`OutputMemoDTO` に詰めてPresenterに返す

です。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
-       result: MemoData = self.repository.get(memo_id)
+       m: Memo = self.repository.get(memo_id)
+       output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id,memo=m.memo,memo_author=m.memo_author)
-       return self.presenter.create_view_for_get(result)
+       return self.presenter.create_view_for_get(output)

-   def save(self, memo_data: MemoData):
+   def save(self, input_memo_dto: InputMemoDTO):
+       m = Memo(memo_id=input_memo_dto.memo_id,memo=input_memo_dto.memo,memo_author=input_memo_dto.memo_author,memo_user_agent=input_memo_dto.memo_user_agent)
-       self.repository.save(memo_data)
+       self.repository.save(m)

        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:
-           result: MemoData = self.repository.get(day_number)
+           m: Memo = self.repository.get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

+       output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id,memo=m.memo,memo_author=m.memo_author)

-       return self.presenter.create_view_for_get_by_day(result)
+       return self.presenter.create_view_for_get_by_day(output)


```

また、DBレイヤーでは、DTOではなく、Entityを用いて値を返すことで、
DBのデータ構造をそのまま返すようにします。

*frameworks_drivers/db/mysql.py*
```python
class Mysql(MemoRepositoryGateway):
    ...
-   def get(self, memo_id: int) -> MemoData:
-   def get(self, memo_id: int) -> Memo:
        ...
-       return Memo(memo_id=memo_id, memo=result[1], memo_author=result[2])
+       return Memo(memo_id=memo_id, memo=result[1], memo_author=result[2],memo_user_agent=result[3])
    ...
```

これにより、秘匿性の高い情報を、外部に公開しないような設計を取ることができます。

##### ⅴ. Enterprise Business Rules 層: Value Object の採用

ここで、

`メモの著者名を保存するとき、前後のスペースをカットしてほしい。` 

という仕様変更依頼を受けたとします。

下記が前後のスペースをカットする処理ですが、これをいづれかのレイヤーで採用する必要がありそうです。
```
memo_author.split()
```

---

どのレイヤーに配置するかですが、なるべく汎用性の高いレイヤーに配置したいです。

このとき、先程配置したEntityは、どのレイヤーでも汎用的に採用されています。
よって、Entityに配置することで、後に今回の仕様に変更が入った場合でも、修正箇所が少なくて良さそうです。

仮にController層に配置したり、Application Business Rules 層に配置した際、
それぞれのレイヤーには複数のClassが存在することが考えられるため、仕様変更時の修正箇所が多くなりそうです。

*enterprise_business_rules/entity/memo.py*

```python
class Memo(object):

    def __init__(self, memo_id, memo, memo_author, memo_user_agent):
        ...
+       self.__memo_author = memo_author.strip()
        ...
```

---
しかし、

**「プラチナメモ」機能を追加してほしい!**

という依頼が来たとするとどうでしょう

プラチナメモ機能は、通常のメモ機能に搭載している

- memo_id
- memo
- memo_author
- memo_user_agent

以外に、

`memo_buffer`

というプロパティを持ち、このプロパティには下書きを保存できるようにするとします。

このとき、

`Memo` Entityとは別に、新たに `PlatinumMemo` Entity を作成するとします。


```python
class PlatinumMemo(object):

    def __init__(self, memo_id, memo, memo_author, memo_user_agent, memo_buffer):
        ... 
        self.__memo_id = memo_id
        self.__memo = memo
        self.__memo_author = memo_author.strip()
        self.__memo_user_agent = memo_user_agent
+       self.__memo_buffer = memo_buffer
        ...

```

このとき、先程追加した `著者名の前後の空白を削除する` という機能を、
`Memo` Entityとは別に、この `PlutinumMemo` Entity にも追記する必要があります。

このケースのように、既存の Entity に記載している処理を、
別の目的で新たに生成した Entityに、再度記載しなければならないケースがあります。

今回は **メモの前後の空白を削除する** というシンプルな機能ですが、
これがメールアドレスのvalidateや、電話番号のvalidateになると、
新たなEntityを生成するたびに、これらを転機しなければなりません。

---

今回の **メモの前後の空白を削除する** は、
`memo_author` 単体に対して行われる処理です。

そのため、`memo_author` に対する処理として、`strip()` をカプセル化し、
それを各Entityから呼び出す形式にすると、今回のように各Entity内に、プロパティの加工・Validationを追記しなくて良さそうです。

そのカプセル化を担うのが、ValueObjectです。

*enterprise_business_rules/value_object/memo_author.py*

```python
class MemoAuthor(str):

    def __new__(cls, memo_author):
        if not type(memo_author) is str:
            raise TypeError('Argument is not str.')
        
        memo_author = memo_author.strip()

        self = super().__new__(cls, memo_author)
        return self

```

このMemoAuthorを、Entityでは受け取るようにします。

*enterprise_business_rules/entity/memo.py*

```python
class Memo(object):

    def __init__(self, memo_id, memo, memo_author, memo_user_agent, memo_buffer):
        ...
        assert isinstance(memo_author, MemoAuthor)
        ...

```

そして、`Memo` Entityを扱うときは、このValue Objectを用いて、Entityを生成するようにします。

*application_business_rules/memo_handle_interactor.py*

```python
class MemoHandleInteractor:
    ...
    def save(self, input_memo_dto: InputMemoDTO):
-       m = Memo(memo_id=input_memo_dto.memo_id, memo=input_memo_dto.memo, memo_author=input_memo_dto.memo_author,memo_user_agent=input_memo_dto.memo_user_agent)
+       m = Memo(memo_id=input_memo_dto.memo_id, memo=input_memo_dto.memo, memo_author=MemoAuthor(input_memo_dto.memo_author),memo_user_agent=input_memo_dto.memo_user_agent)
        self.repository.save(m)
        return self.presenter.create_view_for_save()
    ...
```

これにより、`memo_author` に対する個別の加工 or validateの処理を、Entityから切り離すことができます。

Entity内で採用するValue Objectが増えてくると、可読性が落ちていきます。
そのようなケースでは、Factoryパターン等を採用し、その中でDTOからEntityへのMappingを行うなどの方法があります。

## 4. 設計の変化によって、どのような仕様変更に耐えうるようになったか?
データベースと同構造のオブジェクト、Entityを用いて、DBとのやりとりを行い、
秘匿性の高いプロパティを隠蔽するために、各Business Rules内でDTOを採用する設計にしました。

これにより、各Business Rules で、DB内の各プロパティを柔軟に扱うことができる設計となりました。

また、各プロパティのvalidate・加工処理を、ValueObjectを採用して、Entityから独立させました。
これにより、Entityを新たに生成・変更する場合に、各Entity内で特定のプロパティを意識した実装をしなくても良くなりました。


