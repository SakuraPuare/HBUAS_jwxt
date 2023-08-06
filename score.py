from typing import List, Any

import numpy
import prettytable
from bs4 import BeautifulSoup

from request import Request


class Score:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_score(request: Request, semester: str, **kwargs) -> list[list[str] | list[Any]] | None:
        assert request.is_login
        response = request.get_lesson_score(semester=semester, **kwargs).decode()
        soup = BeautifulSoup(response, 'html.parser')
        # 查找table
        soup = soup.find('table', attrs={'id': 'dataList'})
        # 获取表头
        table = [[th.text for th in soup.find('tr').find_all('th')]]
        # 获取表格内容
        for tr in soup.find_all('tr')[1:]:
            table.append([td.text for td in tr.find_all('td')])
        if table[1] == ['未查询到数据']:
            return None
        return table

    @staticmethod
    def prt_table(field: List[str], data: List[List[str]]) -> None:
        pretty = prettytable.PrettyTable()
        pretty.field_names = field
        for row in data:
            pretty.add_row(row)
        print(pretty)
        return

    def prt_score(self, request: Request, semester: str, **kwargs) -> None:
        table = self.get_score(request, semester, **kwargs)
        self.prt_table(table[0], table[1:])

    def cac_score(self, request: Request, semester: str, **kwargs) -> float:
        score = self.get_score(request, semester, **kwargs)
        assert score is not None

        # remove the public elective course
        score = [i for i in score[1:] if i[9] != '公选']

        value = numpy.array([float(i[4]) for i in score])
        credit = numpy.array([float(i[5]) for i in score])
        return numpy.sum(value * credit) / numpy.sum(credit)


if __name__ == '__main__':
    rq = Request()
    rq.login()
    sc = Score()
    score1 = sc.get_score(rq, '2022-2023-1')
    score2 = sc.get_score(rq, '2022-2023-2')
    print(numpy.average([sc.cac_score(rq, '2022-2023-1'), sc.cac_score(rq, '2022-2023-2')]))
    sc.prt_table(score1[0], score1[1:])
    sc.prt_table(score2[0], score2[1:])
