import io
from typing import Union

import pandas


class Lesson:
    def __init__(self, name: str = '', teacher: str = '', time: str = '', location: str = ''):
        self.name: str = name
        self.time = self._fmt_time(time) if time else []
        self.location = self._fmt_location(location) if location else ''
        self.teacher = self._fmt_teacher(teacher) if teacher else []

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
    def _fmt_teacher(s: str) -> list[str]:
        return [i.replace('()', '') for i in s.split(',') if i != '']

    @staticmethod
    def _fmt_time(s: str) -> list:
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


def load_schedule_table(byte: Union[bytes, io.IOBase]) -> dict:
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
                lesson_dict[day][index - 2] = lesson_list
    return lesson_dict


if __name__ == '__main__':
    load_schedule_table()
