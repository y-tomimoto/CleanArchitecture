# Part9: テスト可能~まとめ
さて、Part8では、DDDにおけるEntityとValue Objectを、Enterprise Busines Rules層に導入しました。

この記事では、前回の章で作成した下記のコードをベースとして解説を進めています。

> Part9:
 
## CleanArchitectureを段階的に適用して得られた各メリットを提示

さて、ここまでに、シンプルなAPIに、段階的に CleanArchitecture を適用してきました。

ここで、導入したレイヤーごとに、どのような変更に強くなったのかをまとめてみましょう。

#### [Part2: Frameworks & Drivers 層: Web の登場](TODO:URLを追加)

採用したい各Webアプリケーションフレームワークを、Frameworks & Drivers 層: Web に切り出し、本来アプリケーションに期待する処理を `MemoHandler` に切り出したことで、
採用したい router を、`main.py` で呼び出すだけで、**アプリケーションに本来期待する処理である、`memo_handler.py` に手を入れることなく、フレームワークを柔軟に変更** できる設計としました。

この設計では、CleanArchitecture のルールの 1 つ、**フレームワーク独立** が実現されています。

> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> フレームワーク独立: アーキテクチャは、機能満載のソフトウェアのライブラリが手に入ることには依存しない。これは、そういったフレームワークを道具として使うことを可能にし、システムをフレームワークの限定された制約に押し込めなければならないようなことにはさせない。

#### [Part3: Enterprise Business Rules 層 & Application Business Rules 層の登場](TODO:URLを追加)

アプリケーションに本来期待する処理が記載された `memo_handler.py`を 

- Enterprise Business Rules
- Application Business Rules

に分割しました。

これにより、`memo_handler.py` を、
1. アプリケーションにおける原則的な処理と、
2. それらを活用してアプリケーションの仕様を満たす流動的な処理

に分割することで、アプリケーションの仕様変更の際、既存の原則的な処理に影響を与えず、仕様を柔軟に修正・拡張できる設計になりました。

#### [Part4: Interface Adapters 層: Controllers の登場](TODO:URLを追加)

Interface Adapters 層の Controller を活用することによって、
更新頻度の高い、『外部からのリクエスト形式』を、実際の処理に適した形式に変更するという部分を、
フレームワークから切り出すことができました。

これにより、アプリケーションで受け入れることのできるリクエストの形式を変更する際、
既存のWebアプリケーションフレームワークや、ビジネスルールを考慮せずに、コードの修正を行うことができるような設計になりました。

#### [Part5: ~番外編~ DTOの活用](TODO:URLを追加)
DTOを採用することで、レイヤー間のデータアクセスを円滑にすると同時に、
アプリケーションで扱うデータ構造が変化した際に、各レイヤーへの影響を最小限に抑えられるような設計になりました。

#### [Part6: Interface Adapters 層: Presenter の登場](TODO:URLを追加)
Presenter の実装に加えて、OutputPort の実装も行いました。

これにより、UIを変更する際、既存のWebアプリケーションフレームワークや、ビジネスルールを考慮せず、UIのみ を独立して変更できる設計になりました。


このPresenterの導入により、CleanArchitecture のルール、UI独立が達成されています。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> UIは、容易に変更できる。システムの残りの部分を変更する必要はない。たとえば、ウェブUIは、ビジネスルールの変更なしに、コンソールUIと置き換えられる。

#### [Part7: Frameworks & Drivers 層: DB と Interface Adapters 層: Gateways の登場](TODO:URLを追加)
DBレイヤーにDBを実装し、Gatawaysを採用しました、

これにより、DBの変更を行う際、各レイヤーを考慮せずに、DBを切り替えることのできる設計となっています。

これより、CleanArchitecture のルール、データベース独立が達成されています。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> データベース独立。OracleあるいはSQL Serverを、Mongo, BigTable, CoucheDBあるいは他のものと交換することができる。ビジネスルールは、データベースに拘束されない。

#### [Part8: Enterprise Business Rules 層: Entity & Value Object の採用](TODO:URLを記載)
データベースと同構造のオブジェクト、Entityを用いて、DBとのやりとりを行い、
秘匿性の高いプロパティを隠蔽するために、各Business Rules内でDTOを採用する設計にしました。

これにより、各Business Rules で、秘匿性を持つプロパティを意識せず、DB上の値を扱うことができる設計となりました。

また、各プロパティのvalidate・加工処理を、ValueObjectを採用して、Entityから独立させました。
これにより、Entityを新たに生成・変更する場合に、各Entity内で特定のプロパティを意識した実装をしなくても良くなりました。


## テスト可能

#### CleanArchitectureのルールの達成
ここまでに、外部機能である Webアプリケーションフレームワーク、DB、UIのいづれを変更しても、内部の
- Application Business Rules 層
- Enterprise Business Rules 層
を変更する必要はありません。

つまり、それぞれの外部機能が独立してると言えます。

これは、CleanArchitectureのルール、外部機能独立を達成していると言えます。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> 外部機能独立。実際のところ、ビジネスルールは、単に外側についてなにも知らない。
 
---

CleanArchitectureのルールは5つ存在します。
> クリーンアーキテクチャ(The Clean Architecture翻訳) :https://blog.tai2.net/the_clean_architecture.html
>> 1. フレームワーク独立。アーキテクチャは、機能満載のソフトウェアのライブラリが手に入ることには依存しない。これは、そういったフレームワークを道具として使うことを可能にし、システムをフレームワークの限定された制約に押し込めなければならないようなことにはさせない。
>> 2. テスト可能。ビジネスルールは、UI、データベース、ウェブサーバー、その他外部の要素なしにテストできる。
>> 3. UI独立。UIは、容易に変更できる。システムの残りの部分を変更する必要はない。たとえば、ウェブUIは、ビジネスルールの変更なしに、コンソールUIと置き換えられる。
>> 4. データベース独立。OracleあるいはSQL Serverを、Mongo, BigTable, CoucheDBあるいは他のものと交換することができる。ビジネスルールは、データベースに拘束されない。
>> 5. 外部機能独立。実際のところ、ビジネスルールは、単に外側についてなにも知らない。

現在までに、2番以外については達成されています。

では、このテスト可能は達成されているのでしょうか??

#### テスト可能は達成されているか?

結論からいうと達成されています。

`ビジネスルールは、UI、データベース、ウェブサーバー、その他外部の要素なしにテストできる。`

という文言についてです。

ここでビジネスルールを確認してみましょう。
このクラスをインスタンス化してテストを行うにあたり、`presenter` と `repository` が必要かと思います。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository

    def get(self, memo_id):
        m: Memo = self.repository.get(memo_id)
        output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id, memo=m.memo,
                                              memo_author=m.memo_author)
        return self.presenter.create_view_for_get(output)

    def save(self, input_memo_dto: InputMemoDTO):
        m = Memo(memo_id=input_memo_dto.memo_id, memo=input_memo_dto.memo, memo_author=MemoAuthor(input_memo_dto.memo_author),
                 memo_user_agent=input_memo_dto.memo_user_agent)
        self.repository.save(m)
        return self.presenter.create_view_for_save()

    def get_by_day_number(self) -> str:
        # 日付を取得する
        dt_now = datetime.datetime.now()
        day_number: int = dt_now.day
        try:

            m: Memo = self.repository.get(day_number)
        except NotFound:
            raise NotFound(f'本日 [{day_number}] 日のメモはまだ登録されていません。')

        output: OutputMemoDTO = OutputMemoDTO(memo_id=m.memo_id, memo=m.memo,
                                              memo_author=m.memo_author)

        return self.presenter.create_view_for_get_by_day(output)

```

このとき、`〜その他外部の要素なしにテストできる` という条件を満たしていないと思うかもしれませんが、
ニュアンスとしては、`〜その他外部の要素の実態なしにテストできる`という捉え方をすると、スムーズに理解できるかと思います。

例えばですが、本来は、コンストラクタに対して、`AdPresenter` 、`Mysql` インスタンスを渡しています。
テスト時に、`MemoHandlerInteractor`に対して、これらのインスタンスを渡すと、それぞれのインスタンスが正常に動作していなけば、`MemoHandlerInteractor`自体のテストができません。

*application_business_rules/memo_handle_interactor.py*
```python
class MemoHandleInteractor:
    def __init__(self, presenter: MemoOutputPort, repository: MemoRepositoryGateway):
        self.presenter = presenter
        self.repository = repository
    ...
```

しかし、コンストラクタの型には、`MemoOutputPort`を採用しているため、
 `MemoOutputPort` を実装している、実態のないテスト用のPresneterを、`MemoHandleInteractor`のコンストラクタとして採用することができます。
Repositoryについても同様です。

*テスト用のRepository*
```python
class TestRepository(MemoRepositoryGateway):
    def exist(self, memo_id: int) -> bool:
        return True

    def get(self, memo_id: int) -> Memo:
        return Memo(memo_id=99, memo="test", memo_author="test",memo_user_agent="test")

    def save(self, m: Memo) -> bool:
        return True
```

このような、テストダブルを用いて、ビジネスロジックを司る `MemoHandleInteractor`をテストすることが可能です。

> テストダブル - Wikipedia: https://ja.wikipedia.org/wiki/%E3%83%86%E3%82%B9%E3%83%88%E3%83%80%E3%83%96%E3%83%AB
>> テストダブル (Test Double) とは、ソフトウェアテストにおいて、テスト対象が依存しているコンポーネントを置き換える代用品のこと。ダブルは代役、影武者を意味する

これにより、これまでのPartを通じて、テスト可能を含む全てのCleanArchitectureのルールが、このアプリケーションでは達成されていると言えます。

※ 注略
下記のCleanArchitectureの図の中で、どのPartでも唯一登場していない、Input Port があります。
これは、InteractorのInterfaceであり、Controller層で、Interactorテストダブルを採用するためのInterfaceです。

今回の記事では、Controller層のテスタビリティを担保すること、そして、Interactorの多態性を担保することのメリットを構成上省いていますが、
Part9のコードでこっそり追加しているので、確認してみてください。


# まとめ

これまでに、各Partを通じて、CleanArchitectureの設計を適用し、設計のメリットを具体的にコードと共に明示しました。

CleanArchitectureは、表面的には難しいワードや、難解な設計となっていても、
結局の所、突き詰めて言えばSOLID原則を忠実に守るための手段でしかないなと感じました。

CleanArchitectureを採用するメリット自体は、SOLID原則に集約されています。
なので、CleanArchitectureを知らないが、SOLID原則を忠実に守る100人の設計者に、アプリケーションの設計を依頼したとき、
いくつかの設計は CleanArchitecture に親しいものになっているのだと思います。