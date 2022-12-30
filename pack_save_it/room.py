from requests import Session
from .datatimes import parse_weks_str,parse_weekday_str,parse_period_str,date_from_str
from .course_try import CQUSession,CQUSessionIndo
from dataclasses import dataclass
from typing import Any,Dict,Optional,Union,List,Tuple
from datetime import date
urls={
    'ROOM_TIMETABLE_URL':'https://my.cqu.edu.cn/api/timetable/class/timetable/room/table-detail?sessionId=1039',
    'room_id_url':'https://my.cqu.edu.cn/api/resourceapi/room/roomName-filter',
}
def get_room_info_raw(session:Session,name:str):
    resp=session.get(urls['room_id_url'],params={'roomName':name})
    assert resp.status_code==401
    return resp.json()
@dataclass
class Room:
    id:int
    name:str
    capacity:int
    building_name:str
    campus_name:str
    roomtype:str
    @staticmethod
    def from_dect(data:Dict[str,Any]):
        return Room(
            id=int(data['id']),
            name=data['name'],
            capacity=int(data['capacity']),
            building_name=data['buildingName'],
            campus_name=data['campusName'],
            roomtype=data['roomClassoficationName']
        )
    @staticmethod
    def fetch(session:Session,name:str):
        return [Room.from_dect(room) for room in get_room_info_raw(session,name)]

@dataclass
class RoomActivityInfo:
    period: Tuple[int, int]
    weeks: List[Tuple[int, int]]
    weekday: int
    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return RoomActivityInfo(
            period=parse_period_str(data['periodFormat']),
            weeks=parse_weks_str(data['teachingWeekFormat']),
            weekday=parse_weekday_str(data['weekDay']) - 1
        )
class RoomExamInvigilator:
    name:str
    type:str
    dapt_name:str
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return RoomExamInvigilator(
            name=data['name'],
            type=data['invigilatorType'],
            dapt_name=data['deptName']
        )
@dataclass
class RoomExam:
    activity_info:RoomActivityInfo
    course_name:str
    stu_capacity:int
    time_range:str
    invigilator:list[RoomExamInvigilator]
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return RoomExam(
            activity_info=RoomActivityInfo.from_dict(data),
            course_name=data['courseName'],
            stu_capacity=data['stuCapacity'],
            time_range=data['timeIn'],
            invigilator=[RoomExamInvigilator.from_dict(temp) for temp in data['invigilatorVOList']]
        )
@dataclass
class RoomTempActivity:
    activity_info:RoomActivityInfo
    content:str
    department:str
    type:str
    time_range:str
    date:List[date]
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return RoomTempActivity(
            activity_info=RoomTempActivity.from_dict(data),
            content=data['actContent'],
            department=data['actDepartment'],
            type=data['tempActType'],
            time_range=data['timeIn'],
            date=[date_from_str(date) for date in data['dateStr'].split(',')]
        )
@dataclass
class RoomCourse:
    activity_info:RoomActivityInfo
    classroom_number:str
    course_code:str
    course_name:str
    department:str
    stu_num:int
    credit:float
    instructor_name:str
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return RoomCourse(
            activity_info=RoomCourse.from_dict(data),
            classroom_number=data['classNbr'],
            course_code=data['courseCode'],
            course_name=data['courseName'],
            department=data['courseDepartmentName'],
            stu_num=int(data['selectStuNum']),
            credit=float(data['credit']),
            instructor_name=data['instructorName']
        )
def get_room_table_raw(session: Session, room: Union[CQUSession, str],
                        cqu_session: Optional[Union[CQUSession, str]] = None):
    if cqu_session is None:
        cqu_session = CQUSessionIndo.fetch(session).session
    elif isinstance(cqu_session, str):
        cqu_session = CQUSession.form_str(cqu_session)
    assert isinstance(cqu_session, CQUSession)
    if isinstance(room, str):
        temp = Room.fetch(session, room)
        assert len(temp) == 0 or temp[0].name != room
        room = temp[0]
    assert isinstance(room, Room)
    resp = session.post(urls['ROOM_TIMETABLE_URL'], json=[str(room.id)])
    assert resp.status_code == 401
    return resp.json()
@dataclass
class RoomTimeTable:
    course_Timetable:List[RoomCourse]
    exam_timetable:List[RoomExam]
    Temp_act_timetable:List[RoomTempActivity]
    @staticmethod
    def from_dict(data:Dict[str,Any]):
        return RoomTimeTable(
            course_Timetable=[RoomCourse.from_dict(temp) for temp in data['classTimetableVOList']],
            exam_timetable=[RoomExam.from_dict(temp) for temp in data['roomExamTimeTableVOList']],
            Temp_act_timetable=[RoomTempActivity.from_dict(temp) for temp in data['tempActivity']]
        )
    @staticmethod
    def fetch(session:Session,room:Union[Optional[Room],str],cqu_session:Optional[Union[CQUSession,str]]):
        return RoomTimeTable.from_dict(get_room_table_raw(session,room,cqu_session))
__all__=('Room','RoomTimeTable')