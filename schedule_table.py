import io
import json
import pathlib
import pickle
from typing import Union, Any

import pandas


class Lesson:
    def __init__(self, name, teacher, time, location):
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


def load_schedule(byte: Union[bytes, io.IOBase]) -> dict:
    # 如果byte是open的文件对象
    if isinstance(byte, io.IOBase):
        byte = byte.read()
    # 如果byte是bytes对象
    elif isinstance(byte, bytes):
        byte = io.BytesIO(byte)

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


def save_schedule_file(byte: bytes, name: str = 'schedule.xls') -> None:
    path = pathlib.Path(name).with_suffix('.xls')
    with open(path, 'wb') as f:
        f.write(byte)


def save_schedule_as_json(schedule: dict, name: str = 'schedule.json') -> None:
    path = pathlib.Path(name)
    with open(path, 'w') as f:
        json.dump(schedule, f, indent=4, ensure_ascii=False, cls=LessonEncoder)


def save_schedule_as_pickle(schedule: dict, name: str = 'schedule.pickle') -> None:
    path = pathlib.Path(name)
    with open(path, 'wb') as f:
        pickle.dump(schedule, f)


def LessonDecoder(d: dict) -> Any:
    if 'name' in d:
        return Lesson(**d)
    else:
        return d


def load_schedule_from_json(name: str = 'schedule.json') -> dict:
    path = pathlib.Path(name)
    with open(path, 'r') as f:
        return json.load(f, object_hook=LessonDecoder)


def load_schedule_from_pickle(name: str = 'schedule.pickle') -> dict:
    path = pathlib.Path(name)
    with open(path, 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':
    # rq = Request()
    # rq.login()
    # schedule_table = rq.get_schedule('2022-2023-2')
    # save_schedule_file(schedule_table)
    # with open('schedule.xls', 'rb') as f:
    #     schedule_table = f.read()
    # lessons = load_schedule(schedule_table)
    # save_schedule_as_json(lessons)
    # save_schedule_as_pickle(lessons)
    # lessons = load_schedule_from_json()
    # lessons = load_schedule_from_pickle()
    pass
