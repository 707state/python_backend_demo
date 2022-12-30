from typing import Callable
from requests import Response

__all__ = (
"CQUWebsiteError", "NotAllowedService", "NeedCaptcha", "InvalidCaptha", "IncorrectLoginCredentials", "TicketGetError",
"ParseError", "MycquUnauthorized",
"UnknownAuthserverExcepyion", "NotLogined", "MultiSessionConflict")


class MycquException(Exception):
    pass


class CQUWebsiteError(MycquException):
    def __init__(self, error_msg="No error info"):
        super().__init__("CQU Website Return Error: " + error_msg)


class NotAllowedService(MycquException):
    pass

class NeedCaptcha(MycquException):
    def __init__(self, image: bytes, image_type: str, after_captcha: Callable[[str], Response]):
        self.image: bytes = image
        """验证码图片文件数据"""
        self.image_type: str = image_type
        """验证码图片类型"""
        self.after_captcha: Callable[[str], Response] = after_captcha
        """将验证码传入，调用以继续登录"""


class InvalidCaptha(MycquException):
    def __init__(self):
        super().__init__("invalid captcha")


class IncorrectLoginCredentials(MycquException):
    def __init__(self, *args: object) -> None:
        super().__init__("incorrect username or password")


class TicketGetError(CQUWebsiteError):
    pass

class ParseError(CQUWebsiteError):
    pass

class UnknownAuthserverExcepyion(CQUWebsiteError):
    pass


class NotLogined(MycquException):
    def __init__(self):
        super().__init__("not in logined status")


class MultiSessionConflict(MycquException):
    def __init__(self, kick: Callable[[], Response], cancel: Callable[[], Response]):
        super().__init__("单处登录 enabled, kick other sessions of the user or channel")
        self.kick: Callable[[], Response] = kick
        self.cancel: Callable[[], Response] = cancel


class MycquUnauthorized(MycquException):
    def __init__(self):
        super().__init__("Unauthorized in mycqu, auth.login first and then mycqu.access_mycqu")


class InvalidRoom(MycquException):
    def __init__(self):
        super().__init__("Invalid Room Name")