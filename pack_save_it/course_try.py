import re
from datetime import date
from dataclasses import dataclass
from requests import Session,get
from .datatimes import datetime_from_str,date_from_str,time_fome_str,parse_period_str,parse_weekday_str,parse_weks_str
from typing import Optional,Tuple,Any,List,Union,ClassVar,Dict
from functools import lru_cache
from .exception import CQUWebsiteError
urls={
    'CQUSESSIONS_URL':'https://my.cqu.edu.cn/api/timetable/optionFinder/session?blankOptional=false',
    'CUR_SESSION_URL':'https://my.cqu.edu.cn/api/resourceapi/session/cur-active-session',
    'ALL_SESSIONS_INFO_URL':'https://my.cqu.edu.cn/api/resourceapi/session/list',
    'TIME_TABLE_URL':'https://my.cqu.edu.cn/api/timetable/class/timetable/student/table-detail'
}
@dataclass
class CQUSession:
    year:int
    is_autumn:bool
    SESSION_RE:ClassVar=re.compile("^([0-9]{4})年?(春|秋)$")
    _SPECIAL_IDS:ClassVar[Tuple[int,...]]=(
        239259,102,101,103,1028,1029,1030,1032#要去查一查
    )
    @lru_cache(maxsize=32)
    def __new__(cls,year:int,is_autumn:bool):
        return super(CQUSession,cls).__new__(cls)
    def __str__(self):
        return str(self.year)+('秋' if self.is_autumn else '春')
    def get_id(self)->int:
        if self.year>=2019:
            return (self.year-1503)*2+int(self.is_autumn)+1
        elif self.year>=2015 and self.year<2019:
            return self._SPECIAL_IDS[(self.year-2015)*2+int(self.is_autumn)]
        else:
            return (2015-self.year)*2-int(self.is_autumn)
    @staticmethod
    def form_str(string:str):
        match=CQUSession.SESSION_RE.match(string)
        if match:
            return CQUSession(
                year=match[1],
                is_autumn=match[2]=='秋'
            )
        else:
            raise ValueError(f'string {string} is not a session')
    @staticmethod
    def fetch():
        session_list=[]
        session_get=get(urls['CQUSESSIONS_URL'])
        for session in session_get.json():
            if session_get.status_code ==200:
                session_list.append(CQUSession.form_str(session['name']))
            else :
                raise CQUWebsiteError()
            return session_list
@dataclass
class CQUSessionIndo:
    session:CQUSession
    begin_data:date
    end_date:date
    @staticmethod#在不创建实力的情况下调用
    def from_dict(session:CQUSession,data:Dict[str,Any])->Any:
        if session.is_autumn:
            return CQUSessionIndo(
                session=CQUSession(
                    year=data['year'],
                    is_autumn=1,),
                    begin_data=date_from_str(data['beginDate']),
                    end_date=date_from_str(data['endData']),
            )
        else:
            return CQUSessionIndo(
                session=CQUSession(
                    year=data['year'],
                    is_autumn=0
                ),
                begin_data=date_from_str(data['beginDate']),
                end_date=date_from_str(data['endDate']))
    @staticmethod
    def fetch_all(session:Session):
        resp=session.get(urls['ALL_SESSIONS_INFO_URL'])
        assert resp.status_code!=401
        cqussions:List[CQUSessionIndo]=[]
        for data in resp.json['sessionVOList']:
            if not data['beginData']:
                break
            cqussions.append(CQUSessionIndo.from_dict(data))
        return cqussions
    @staticmethod
    def fetch(session:Session):
        resp=session.get(urls['CUR_SESSION_URL'])
        assert resp.status_code !=401
        return CQUSessionIndo.from_dict(resp.json()['data'])
@dataclass
class CourseDayTime:
    weekday:str
    period:Tuple[int,int]
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        if data.get('periodFormat') and data.get("weekDayFormat"):
            return CourseDayTime(
                weekday=str(parse_weekday_str(data['weekDayFormat'])),
                period=parse_period_str(data['periodFormat'])
            )
        return None
@dataclass
class Course:
    name:str
    code:str
    course_name:Optional[str]
    depth:Optional[str]
    credit:Optional[float]
    instructor:Optional[str]
    session:Optional[CQUSession]
    @staticmethod
    def from_dict(self,data:Dict[str,Any],session:Optional[Union[str,CQUSession]]=None):
        if session is None and not data.get('session') is None:
            session=CQUSession.form_str(data['session'])
        if isinstance(session,str):
            session=CQUSession.form_str(session)
        assert isinstance(session,CQUSession) or session is None
        instructor_name=data.get('instructorName') if data.get('instructorName') is not None else \
            ", ".join(self.instructor.get('instructorName'))
        return Course(
            name=data['courseName'],
            code=data['courseCode'],
            course_name=data.get('classNbr'),
            depth=data.get('courseDepartmentName') or data.get('courseDeptShortName'),
            credit=data.get('credit') or data.get('courseCredit'),
            session=session
        )
def _get_course_raw(session:Session,code:str,cqu_session:Optional[Union]):
    if cqu_session is None:
        cqu_session=CQUSessionIndo.fetch(session).session
    elif isinstance(cqu_session,str):
        cqu_session=CQUSession.form_str(cqu_session)
    assert isinstance(cqu_session,CQUSession)
    resp=session.post(urls['TIME_TABLE_URL'],
    params={'sessionId':cqu_session.get_id()},json=[code])
    assert resp.status_code1!=401
    return resp.json()['classTimetableVOList']
@dataclass
class CourseTimetable:
    course:Course
    stu_num:Optional[int]
    classroom:Optional[str]
    weeks:List[Tuple[int,int]]
    day_time:Optional[CourseDayTime]
    whole_week:bool
    classroom_name:Optional[str]
    expr_projects:List[str]
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return CourseTimetable(
            course=Course.from_dict(data),
            stu_num=data.get('selectedStuNum'),
            classroom=data.get('position'),
            weeks=parse_weks_str(data.get('weeks') or data.get('teachingWeekFormat')),
            day_time=CourseDayTime.from_dict(data),
            whole_week=bool(data['wholeWeekOccupy']),
            classroom_name=data['roomName'],
            expr_projects=(data['exprProjectName'] or ' ').split(',')
        )
    @staticmethod
    def fetch(session:Session,code:str,cqu_session:Optional[Union[CQUSession,str]]=None):
        resp=_get_course_raw(session,code,cqu_session)
        dic_=[]
        for timetable in resp:
            if timetable['teachingWeekFormat']:
                dic_.append([CourseTimetable.from_dict(timetable),timetable['teachingWeekFormat']])
        return dic_