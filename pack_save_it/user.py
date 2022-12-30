from requests import Session
from dataclasses import dataclass
#dataclass的作用是一个装饰器，减少了构造函数的调用
from .exception import MycquUnauthorized
_url="https://my.cqu.edu.cn/authserver/simple-user"
@dataclass
class User:
    name:str
    uniform_id:str
    code:str
    role:str
    email:str#Optional?
    phone_number:str
    @staticmethod
    def fetch_self(session:Session):
        resp=session.get(url=_url)
        if resp.status_code==401:
            raise MycquUnauthorized()
        data=resp.json()
        return User(
            name=data['name'],
            code=data['code'],
            uniform_id=data['userna,e'],
            role=data['type'],
            email=data['email'],
            phone_number=data['phoneNumber']
        )
__all__=('User')