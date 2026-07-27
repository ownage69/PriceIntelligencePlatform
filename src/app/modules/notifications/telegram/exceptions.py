class TelegramBaseError(Exception):
    pass


class TelegramNetworkError(TelegramBaseError):
    pass


class TelegramAPIError(TelegramBaseError):
    pass


class TelegramRateLimitError(TelegramAPIError):
    
    def __init__(self, message: str, retry_after: int = 1):
        super().__init__(message)
        self.retry_after = retry_after


class TelegramAuthError(TelegramAPIError):
    pass


class TelegramBadRequestError(TelegramAPIError):
    pass
