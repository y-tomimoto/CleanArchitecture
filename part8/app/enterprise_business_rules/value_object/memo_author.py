class MemoAuthor(str):

    def __new__(cls, memo_author):
        if not type(memo_author) is str:
            raise TypeError('Argument is not str.')

        memo_author = memo_author.strip()

        self = super().__new__(cls, memo_author)
        return self