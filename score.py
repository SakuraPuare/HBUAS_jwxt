import prettytable
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from request import Request


class Score:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_score(request: Request, semester: str, **kwargs) -> PrettyTable:
        assert request.is_login
        response = request.get_lesson_score(semester=semester, **kwargs).decode()
        soup = BeautifulSoup(response, 'html.parser')
        # 查找table
        soup = soup.find('table', attrs={'id': 'dataList'})
        table = prettytable.PrettyTable()
        # 获取表头
        table.field_names = [th.text for th in soup.find('tr').find_all('th')]
        # 获取表格内容
        for tr in soup.find_all('tr')[1:]:
            table.add_row([td.text for td in tr.find_all('td')])
        return table


if __name__ == '__main__':
    rq = Request()
    rq.login()
    sc = Score()
    s = sc.get_score(request=rq, semester='2022-2023-1')
    print(s)
