import json
import time
from dataclasses import dataclass
from enum import Enum, IntEnum
from itertools import groupby

from requests import Session


@dataclass
class AppointmentAvailable:
    def __getitem__(self, arg):
        return getattr(self, arg)
    date: str
    day_of_week: str
    start: str
    original_msg: dict


class GroupingBy(Enum):
    DATE = 'date'
    DAY_OF_WEEK = 'day_of_week'


class Weekday(IntEnum):
    @staticmethod
    def values():
        return [w.value for w in Weekday]
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class ICBCError(Exception): ...
class ICBCLoginError(ICBCError): ...
class ICBCAvailabilityError(ICBCError): ...

class RoadTestAppointment:
    # TODO: Implement Appointment Lock
    # TODO: Implement Appointment UnLock
    # TODO: Send and Input Verificatioon Code Email/SMS

    def __init__(self, last_name, licence_number, keyword) -> None:
        self._last_name = last_name
        self._licence_number = licence_number
        self._keyword = keyword
        self.__session = Session()
        self.__session.headers = self.__headers()
        self.user = self.__login()


    def __headers(self) -> dict:
        return {
            'sec-ch-ua': 'Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114',
            'pragma': 'no-cache',
            'sec-ch-ua-platform': 'macOS',
            'DNT': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cache-control': 'no-cache, no-store',
            'Expires': '0'}

    def __login(self) -> str:
        login = self.__session.put('https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin',
                                   headers={
                                       'Referer': 'https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver',
                                   },
                                   json={'drvrLastName': self._last_name,
                                         'licenceNumber': self._licence_number,
                                         'keyword': self._keyword})

        if login.status_code == 200:
            self.__session.headers['Authorization'] = login.headers['Authorization']
            return login.content
        raise ICBCLoginError('Couldn`t login', f'Error: {str(login.content, "UTF-8")}')

    def availability(self, weekdays: list[int] = Weekday.values(), grouping_by=GroupingBy.DATE) -> dict[str, AppointmentAvailable]:
        available = self.__session.post(
            'https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments',
            headers={
                'Referer': 'https://onlinebusiness.icbc.com/webdeas-ui/booking'},
            json={
                'aPosID': '8',  # 8 == Marine Drive, create list places method
                'examType': '5-R-1',  # TODO: Get License type
                'examDate': time.strftime("%Y-%m-%d"),
                'ignoreReserveTime': 'false',  # TODO: Export input, making it default
                'prfDaysOfWeek': f'{weekdays}',
                'prfPartsOfDay': '[0,1]',  # TODO: Export input
                'lastName': self._last_name,
                'licenseNumber': self._licence_number
            })

        def map_to_aa(item): return AppointmentAvailable(item['appointmentDt']['date'],
                                                         item['appointmentDt']['dayOfWeek'],
                                                         item['startTm'],
                                                         item)
        print(available.content)
        if available.status_code == 200:
            available_list = [map_to_aa(item)
                              for item in json.loads(available.content)]
            return {key: list(group) for key, group in groupby(available_list, key=lambda item: item[grouping_by.value])}
        raise ICBCAvailabilityError('Could not fetch dates available', f'Error: {str(available.content, "UTF-8")}')


    def lock(self, appointment: AppointmentAvailable):
        
        
        lock = self.__session.put('https://onlinebusiness.icbc.com/deas-api/v1/web/lock',
                    headers={
                        'Referer': 'https://onlinebusiness.icbc.com/webdeas-ui/booking',
                    },
                    json={'drvrLastName': self._last_name,
                            'licenceNumber': self._licence_number,
                            'keyword': self._keyword})
