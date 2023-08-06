import json
import pathlib
import pickle
from typing import Union, Any

import pandas
from bs4 import BeautifulSoup

from request import Request


class BaseSchedule:
    day_dict = {
        "星期一": "monday",
        "星期二": "tuesday",
        "星期三": "wednesday",
        "星期四": "thursday",
        "星期五": "friday",
        "星期六": "saturday",
        "星期日": "sunday",
    }
    day_list = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    filename = pathlib.Path('schedule')

    def __init__(self):
        self.schedule = None
        self.byte = None

    def load_schedule_from_json(self, name: str = None) -> dict:
        if name is None:
            path = self.filename.with_suffix('.json')
        else:
            path = pathlib.Path(name)
        with open(path, encoding='u8') as f:
            return json.load(f, object_hook=self.LessonDecoder)

    def load_schedule_from_pickle(self, name: str = None) -> dict:
        if name is None:
            path = self.filename.with_suffix('.pickle')
        else:
            path = pathlib.Path(name)
        with open(path, 'rb') as f:
            return pickle.load(f)

    def save_schedule_as_json(self, name: str = None) -> None:
        if name is None:
            path = self.filename.with_suffix('.json')
        else:
            path = pathlib.Path(name)
        with open(path, 'w', encoding='u8') as f:
            json.dump(self.schedule, f, indent=4, ensure_ascii=False, cls=Lesson.LessonEncoder)

    def save_schedule_as_pickle(self, name: str = None) -> None:
        if name is None:
            path = self.filename.with_suffix('.pickle')
        else:
            path = pathlib.Path(name)
        with open(path, 'wb') as f:
            pickle.dump(self.schedule, f)

    def save_schedule_as_xls(self, name: str = 'schedule.xls') -> None:
        if name is None:
            path = self.filename.with_suffix('.xls')
        else:
            path = pathlib.Path(name)
        with open(path, 'wb') as f:
            f.write(self.byte)

    @staticmethod
    def LessonDecoder(d: dict) -> Any:
        if 'name' in d:
            return Lesson(**d)
        else:
            return d


class Schedule(BaseSchedule):
    def __init__(self, schedule) -> None:
        super().__init__()
        self.byte = b''

        if isinstance(schedule, dict):
            self.schedule = schedule
        elif isinstance(schedule, str):
            self.schedule = self.load_from_file(schedule)
        elif isinstance(schedule, bytes):
            self.byte = schedule
            self.schedule = self.load_schedule(schedule)
        else:
            self.schedule = {}

    def load_from_website(self, request: Request, semester: str) -> dict:
        assert request.is_login
        self.byte = request.get_schedule(semester)
        return self.load_schedule(self.byte)

    def load_from_file(self, name: str) -> dict:
        if name.endswith('.xls'):
            with open(name, 'rb') as f:
                self.byte = f.read()
                schedule_ = self.load_schedule(self.byte)
        elif name.endswith('.json'):
            schedule_ = self.load_schedule_from_json(name)
        elif name.endswith('.pickle'):
            schedule_ = self.load_schedule_from_pickle(name)
        else:
            raise ValueError('不支持的文件类型')
        return schedule_

    def load_schedule(self, byte: bytes) -> dict:
        excel = pandas.read_excel(byte, sheet_name='Sheet1')
        lesson_dict = {}
        for column in excel.columns[1:]:
            # 遍历表格每一行
            day = self.day_dict[excel[column][1]]
            lesson_dict[day] = {}
            for index, row in excel[column].items():
                if 1 < index < 7:
                    lesson_list = set()
                    classes_list = row.split('\n\n')
                    for classes in classes_list:
                        if classes == ' ':
                            lesson = Lesson()
                        else:
                            info = [i for i in classes.split('\n') if i != '']
                            lesson = Lesson(*info)
                        lesson_list.add(lesson)
                    lesson_dict[day][index - 2] = list(lesson_list)
        return lesson_dict


class ClassSchedule(BaseSchedule):
    def __init__(self, schedule):
        super().__init__()
        self.byte = b''

        if isinstance(schedule, dict):
            self.schedule = schedule
        elif isinstance(schedule, bytes):
            self.byte = schedule
            self.schedule = self.load_schedule(schedule)
        else:
            self.schedule = {}

    def load_from_website(self, request: Request, semester: str, department: str, grade: str, profession: str,
                          week_start: str = "", week_end: str = "", lesson_start: str = "",
                          lesson_end: str = "") -> dict[dict]:
        assert request.is_login
        self.byte = request.get_class_schedule(semester, department, grade, profession, week_start, week_end,
                                               lesson_start, lesson_end)
        return self.load_schedule(self.byte)

    def load_schedule(self, schedule: bytes) -> dict[dict]:
        soup = BeautifulSoup(schedule, 'html.parser')
        # replace <br> with \n
        for br in soup.find_all('br'):
            br.replace_with('\n')
        data = soup.find_all('tr')[2:]
        l = {}
        for line in data:
            columns = line.find_all('td')
            title = columns[0].text.strip()
            l[title] = {}
            for index in range(0, 7):
                l[title][self.day_list[index]] = []
                for lesson in columns[index * 5 + 1:index * 5 + 6]:
                    for div in lesson.find_all('div'):
                        text = div.text.strip().split()
                        name, teacher, week, location = text[0], text[1], Lesson._fmt_time(text[2][1:], 2), text[3]
                        l[title][self.day_list[index]].append(Lesson(name, teacher, week, location))
        return l


class Lesson:
    def __init__(self, name='', teacher=None, time=None, location: str = ''):
        if teacher is None:
            teacher = []
        if time is None:
            time = []

        self.name: str = name
        self.time = self._fmt_time(time)
        self.location = self._fmt_location(location)
        self.teacher = self._fmt_teacher(teacher)

    def __repr__(self):
        return f'Class({self.name}, {self.teacher}, {self.time}, {self.location})'

    def __str__(self):
        return f"{self.name} {self.teacher} {self.time} {self.location}"

    def __eq__(self, other):
        return self.name == other.name and \
            self.teacher == other.teacher and \
            self.time == other.time and \
            self.location == other.location

    def __bool__(self):
        return bool(self.name)

    def __hash__(self):
        return hash((self.name, tuple(self.teacher), tuple(self.time), self.location))

    @staticmethod
    def _fmt_teacher(s: Union[str, list]) -> list[str]:
        if isinstance(s, list):
            return s
        else:
            return [i.replace('()', '') for i in s.split(',') if i != '']

    @staticmethod
    def _fmt_time(s: Union[str, list], sub: int = 3) -> list:
        if isinstance(s, list):
            return s
        if isinstance(s, int):
            return [s]
        if s != 0:
            s = s[:-sub]
        time = s.split(',')
        t = []
        for week in time:
            if '-' in week:
                start, end = week.split('-')
                t.extend(range(int(start), int(end) + 1))
            else:
                t.append(int(week))
        return t

    @staticmethod
    def _fmt_location(s: str) -> str:
        return s.replace('Ｎ', 'N')

    class LessonEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__


if __name__ == '__main__':
    self = Request()
    self.login()
    schedule = ClassSchedule(self.get_class_schedule('2023-2024-1', '20', '2022', '080605'))
    pass
