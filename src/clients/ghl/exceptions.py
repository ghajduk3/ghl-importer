class GoHighLevelAPIException(Exception):
    pass


class GoHighLevelAPIBadResponseCodeError(GoHighLevelAPIException):
    def __init__(self, message: str, code: int) -> None:
        GoHighLevelAPIException.__init__(self)
        self.message = message
        self.code = code