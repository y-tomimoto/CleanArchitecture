from enterprise_business_rules.value_object.memo_author import MemoAuthor


class Memo(object):

    def __init__(self, memo_id, memo, memo_author, memo_user_agent):
        assert isinstance(memo_id, int)
        assert isinstance(memo, str)
        assert isinstance(memo_author, MemoAuthor)
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
