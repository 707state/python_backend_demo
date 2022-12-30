from typing import List, Tuple, Dict
from datetime import date, time, datetime
import pytz
TIMEZONE=datetime.now(pytz.timezone("Asia/Shanghai")).tzinfo
WEEKDAY:Dict[str, int]= {
    "一":0,
    "二":1,
    "三":2,
    "四":3,
    "五":4,
    "六":5,
    "七":6
}
def time_fome_str(string:str)->time:#设定返回的leiix
    hour, minute= map(int, string.split(":"))#声明为map，构成映射关系
    return time(hour, minute, tzinfo=TIMEZONE)
def parse_period_str(string:str)->Tuple[int,int]:
    period=tuple(map(int, string.split(":")))
    assert len(period) == 1 or len(period) == 2
    """断言：assert exp等价于
    if not exp:
        raise AssertionError
    """
    return period[0],(period[1] if len(period)==2 else period[0])
"""上面返回值进行了简化
"""
def parse_weks_str(string:str)->List[Tuple[int,int]]:
    return [parse_period_str(unit) for unit in string.split(",")]
def parse_weekday_str(string:str)->int:
    return WEEKDAY[string]
def date_from_str(string:str)->date:
    return date.fromisoformat(string)
def datetime_from_str(string:str)->datetime:
    return datetime.strptime(string,'%Y-%m-%d %H:%M:%S').replace(tzinfo=TIMEZONE)
__all__=('datetime','parse_weks_str','parse_weekday_str','date_from_str','datetime_from_str'
,"parse_period_str",'time_fome_str')