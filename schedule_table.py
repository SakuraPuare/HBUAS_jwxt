import io

import pandas


class Lesson:
    def __init__(self, name, teacher, time, location):
        self.name = name
        self.time = self._fmt_time(time)
        self.location = self._fmt_location(location)
        self.teacher = self._fmt_teacher(teacher)

    def __repr__(self):
        return f'Class({self.name}, {self.teacher}, {self.time}, {self.location})'

    def __str__(self):
        return f"{self.name} {self.teacher} {self.time} {self.location}"

    def __hash__(self):
        return hash(self.name + ' '.join(self.teacher) + self.location)

    @staticmethod
    def _fmt_teacher(s: str) -> list:
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


def get_schedule_table() -> str:
    pass


def load_schedule_table(byte: io.BytesIO) -> dict:
    byte = io.BytesIO(byte)
    excel = pandas.read_excel(byte, sheet_name='Sheet1')
    lesson_dict = {}
    for column in excel.columns[1:]:
        # 遍历表格每一行
        day = excel[column][1]
        lesson_dict[day] = {}
        for index, row in excel[column].items():
            if 1 < index < 7:
                classes_list = row.split('\n\n')
                for classes in classes_list:
                    if classes == ' ':
                        continue
                    info = [i for i in classes.split('\n') if i != '']
                    lesson = Lesson(*info)
                    lesson_dict[day][index - 2] = lesson
    return lesson_dict


if __name__ == '__main__':
    load_schedule_table()
