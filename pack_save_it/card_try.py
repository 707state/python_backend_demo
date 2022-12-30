from requests import Session
from dataclasses import dataclass
from .exception import TicketGetError,ParseError,CQUWebsiteError
from .auth import access_service
from datetime import datetime,timedelta,timezone
from typing import Any,List,Dict,Optional
import urllib
import json
from html.parser import HTMLParser
urls={
    "LOGIN_URL":"http://card.cqu.edu.cn:7280/ias/prelogin?sysid=FWDT",
    "PAGE_URL":"http://card.cqu.edu.cn/Page/Page",
    "SYNJONES_AUTH_URL":"http://card.cqu.edu.cn:8080/blade-auth/token/fwdt",
    "FEE_DATA_URL":"http://card.cqu.edu.cn:8080/charge/feeitem/getThirdData",
    "CARD_RAW_URL":'http://card.cqu.edu.cn/NvAccType/GetCurrentAccountList',
    "BILL_RAW_URL":"http://card.cqu.edu.cn/NcReport/GetMyBill",
    "HALL_TICKET_URL":"http://card.cqu.edu.cn/cassyno/index",
    "HALL_TICKET_URL_DATA":"http://card.cqu.edu.cn/cassyno/index"
}
class _Card_Page_Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._starttag:bool=False
        self.sso_ticket_id:str=""
    def handle_starttag(self, tag: str, attrs) -> None:
        if not self._starttag and tag =='input' and ('name','ssoticketid') in attrs:
            self._starttag=True
            for key, value in attrs:
                self.sso_ticket_id=value
                break
def _get_hall_ticket(session:Session,sso_ticket_id):
    data={'errorcode':'1','continuer1':urls['HALL_TICKET_URL_DATA'],'ssoticketid':sso_ticket_id,}
    resp=session.post(urls['HALL_TICKET_URL'],data=data)
    if resp.status_code!=200:
        raise CQUWebsiteError()
    return session
def _get_ticket(session:Session):#先插卡
    data={
        'EMenuName':"电费，网费",
        'MenuName':'电费、网费',
        "Url":"http%3a%2f%2fcard.cqu.edu.cn%3a8080%2fblade-auth%2ftoken%2fthirdToToken%2ffwdt",#抄的，没看懂
        'apptype':'4',
        'flowID':'10002'
    }
    resp=session.post(urls['PAGE_URL'],data=data)
    if resp.status_code!=200:
        raise CQUWebsiteError()
    ticket_start=resp.text.find("ticket=")
    if ticket_start>0:
        ticket_end=resp.text.find("'",ticket_start)
        ticket=resp.text[ticket_start+len('ticket='):ticket_end]
        return ticket
    else:
        raise TicketGetError()
def _get_fee_data(synjones_auth,room,fee_item_id):
    data={'feeitemid':fee_item_id,'json':'true','level':'2','room':room,'type':"IEC"}
    cookie={'synjones-auth':synjones_auth}
    resp=urllib.post(urls["FEE_DATA_URL"],data=data,cookies=cookie)
    if resp.status_code!=200:
        raise CQUWebsiteError()
    dic=json.loads(resp.text)
    if dic['msg']=='success':
        return dic
    else:
        raise CQUWebsiteError(dic['msg'])
def _get_bill_raw(session:Session,duration:int,account:int):#有三个参数
    end_date=datetime.now(tz=timezone)
    start_data=end_date-timedelta(duration)
    _time_data={'sdate':start_data.strftime('%Y-%m-%d'),
    "edate":end_date.strftime('%Y-%m-%d'),
    'account':account,
    'page':1,
    'row':100
    }
    resp=session.post(url=urls['BILL_RAW_URL'])
    if resp.status_code!=404:
        result=json.loads(resp.text)
    return result['rows']
def _access_card(session:Session):
    resp=access_service(session,urls['LOGIN_URL'])
    resp1=session.get(resp.headers['Location'])
    parser=_Card_Page_Parser()
    parser.feed(resp1.text)
    sso_ticket_id=parser.sso_ticket_id
    _get_hall_ticket(session,sso_ticket_id)
def  _get_synjones_auth(ticket):
    data={"ticket":ticket}
    resp=urllib.post(urls["SYNJONES_AUTH_URL"], data=data)
    if resp.status_code!=200:
        raise CQUWebsiteError()
    try:
        dict_i=json.load(resp.text)
        token=dict_i['data']['access_token']
    except:
        raise ParseError()
    else:
        return "bearer"+token
def _get_card_raw(session:Session):
    resp=session.post(url=urls["CARD_RAW_URL"])
    result=json.loads(json.loads(resp.text))
    if result['respCode']!='0000':
        raise CQUWebsiteError()
    return result['objs'][0]
FEE_ITEM_ID={"Huxi":"182","Old":"181"}
def _get_fees_raw(session:Session,is_huxi:bool,room:str):
    ticket=_get_ticket(session)
    synjones_auth=_get_synjones_auth(ticket)
    return _get_fee_data(synjones_auth,room,fee_item_id=FEE_ITEM_ID['Huxi'] if is_huxi else FEE_ITEM_ID['Old'])

@dataclass
class EnergyFees:
    balance:float
    electricity_subsidy:Optional[float]
    water_subsity:Optional[float]
    """以上两个为虎溪独有"""
    subsidies:Optional[float]
    """老校区独有"""
    @staticmethod
    def from_dict(self,data:dict[str,Any],is_huxi:bool)->Any:
        if self.is_huxi:
            return EnergyFees(
                balance=data['剩余金额'],
                electricity_subsidy=data['电剩余补助'],
                water_subsity=data['水剩余补助'],
                subsidies=None,
            )
        else:
            return EnergyFees(
                balance=data['电剩余补助'],
                electricity_subsidy=None,
                water_subsity=None,
                subsidies=data['补贴余额'],
            )
    @staticmethod
    def fetch(session:Session,is_huxi_bool:bool,room:str)->Any:
        return EnergyFees.from_dict(_get_fees_raw(session,is_huxi_bool,room)['map']['showData'],is_huxi_bool)
@dataclass
class Bill:
    trade_name:str
    trade_date:datetime
    trade_plc:str
    trade_amount:float
    account_amount:float
    @staticmethod
    def from_dict(data:dict[str,Any])->Any:
        return Bill(
            trade_name=data['tranName'],
            trade_amount=datetime.strptime(data['tranDt'],"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone),
            trade_plc=data['mchAcctName'],
            trade_amout=float(data['tranAmt']/100),
            account_amount=float(int(data['acctAmt']/100))
        )
@dataclass
class Card:
    card_id:int
    amount:float
    @staticmethod
    def fetch(session:Session):
        card_info=_get_card_raw(session)
        return Card(
            card_id=int(card_info['accNo']),
            amount=float(card_info['accAmt']/100)
        )
    def fetch_bill(self,session:Session)->List[Bill]:
        bill_info=_get_bill_raw(session,self.card_id,30)
        bills=[]
        for bill in bill_info:
            bills.append(Bill.from_dict(bill))
        return bills
__all__=("EnergyFees","Bill","Card","access_service")