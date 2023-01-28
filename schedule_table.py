import json
import pathlib
import pickle
from typing import Union, Any

import pandas

from request import Request


class Schedule:

    def __init__(self, schedule) -> None:
        if isinstance(schedule, dict):
            self.schedule = schedule
        elif isinstance(schedule, str):
            self.schedule = self.load_from_file(schedule)
        elif isinstance(schedule, bytes):
            self.schedule = self.load_schedule(schedule)
        else:
            self.schedule = {}

    def load_from_website(self, request: Request, semester: str) -> dict:
        assert request.is_login
        schedule = request.get_schedule(semester)
        return self.load_schedule(schedule)

    def load_from_file(self, name: str) -> dict:
        if name.endswith('.xls'):
            with open(name, 'rb') as f:
                schedule = self.load_schedule(f.read())
        elif name.endswith('.json'):
            schedule = self.load_schedule_from_json(name)
        elif name.endswith('.pickle'):
            schedule = self.load_schedule_from_pickle(name)
        else:
            raise ValueError('不支持的文件类型')
        return schedule

    @staticmethod
    def load_schedule(byte: bytes) -> dict:
        excel = pandas.read_excel(byte, sheet_name='Sheet1')
        lesson_dict = {}
        for column in excel.columns[1:]:
            # 遍历表格每一行
            day = excel[column][1]
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

    def load_schedule_from_json(self, name: str = 'schedule.json') -> dict:
        path = pathlib.Path(name)
        with open(path, 'r', encoding='u8') as f:
            return json.load(f, object_hook=self.LessonDecoder)

    @staticmethod
    def load_schedule_from_pickle(name: str = 'schedule.pickle') -> dict:
        path = pathlib.Path(name)
        with open(path, 'rb') as f:
            return pickle.load(f)

    def save_schedule_as_json(self, name: str = 'schedule.json') -> None:
        path = pathlib.Path(name)
        with open(path, 'w', encoding='u8') as f:
            json.dump(self.schedule, f, indent=4, ensure_ascii=False, cls=Lesson.LessonEncoder)

    def save_schedule_as_pickle(self, name: str = 'schedule.pickle') -> None:
        path = pathlib.Path(name)
        with open(path, 'wb') as f:
            pickle.dump(self.schedule, f)
    @staticmethod
    def save_schedule_as_xls(byte: bytes, name: str = 'schedule.xls') -> None:
        path = pathlib.Path(name).with_suffix('.xls')
        with open(path, 'wb') as f:
            f.write(byte)

    @staticmethod
    def LessonDecoder(d: dict) -> Any:
        if 'name' in d:
            return Lesson(**d)
        else:
            return d


class Lesson:
    def __init__(self, name='', teacher: Union[str, list] = [], time: Union[str, list] = [], location: str = ''):
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
    def _fmt_time(s: Union[str, list]) -> list:
        if isinstance(s, list):
            return s
        s = s[:-3]
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
    s = Schedule('schedule.xls')
    s.save_schedule_as_json()
    pass
