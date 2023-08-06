import base64

import httpx

from config import Config

config = Config()


class Request:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    def __init__(self):
        self.session = httpx.Client(follow_redirects=True)
        self.base_url = config.page.get('url')

        self.is_login = False

        self.get(self.base_url)

        assert self.session.cookies.get('JSESSIONID') is not None

    @staticmethod
    def encode(s: str):
        return base64.b64encode(s.encode('u8')).decode()

    # @staticmethod
    # def encode(s: str) -> str:
    #     key_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    #
    #     def self_ord(index: int) -> int:
    #         length = len(s)
    #         if index < length:
    #             return ord(s[index])
    #         else:
    #             return 0
    #
    #     output = ""
    #     i = 0
    #     while i < len(s):
    #         chr1 = self_ord(i)
    #         i += 1
    #         chr2 = self_ord(i)
    #         i += 1
    #         chr3 = self_ord(i)
    #         i += 1
    #         enc1 = chr1 >> 2
    #         enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)
    #         enc3 = ((chr2 & 15) << 2) | (chr3 >> 6)
    #         enc4 = chr3 & 63
    #         if not chr2:
    #             enc3 = enc4 = 64
    #         elif not chr3:
    #             enc4 = 64
    #         output = output + key_str[enc1] + key_str[enc2] + key_str[enc3] + key_str[enc4]
    #     return output

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.session.get(url, headers=self.headers, timeout=100, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.session.post(url, headers=self.headers, timeout=100, **kwargs)

    def post_login(self, username: str = config.account.get('username'),
                   password: str = config.account.get('password')) -> httpx.Response:
        username_encoded, password_encoded = self.encode(username), self.encode(password)
        encoded = username_encoded + '%%%' + password_encoded
        data = {'encoded': encoded}
        return self.session.post(self.base_url + 'xk/LoginToXk', headers=self.headers, data=data)

    def get_schedule(self, semester: str) -> bytes:
        url = self.base_url + 'xskb/xskb_print.do'
        data = {'xnxq01id': semester, 'zc': ''}
        response = self.session.get(url, headers=self.headers, params=data)
        assert response.status_code == 200, 'Failed to get schedule'
        return response.content

    def get_class_schedule(self, semester: str, department: str, grade: str, profession: str,
                           week_start: str = "", week_end: str = "", lesson_start: str = "",
                           lesson_end: str = "") -> bytes:
        department_tuple = [('政法学院', '01'), ('教育学院', '02'), ('文学与传媒学院', '03'), ('外国语学院', '04'),
                            ('音乐与舞蹈学院', '05'), ('美术学院', '06'), ('物理与电子工程学院', '08'),
                            ('土木工程与建筑学院', '10'), ('食品科学技术学院·化学工程学院', '11'), ('医学部', '13'),
                            ('创新创业教育学院', '15'), ('体育学院', 'oRZoO6ah6P'), ('数学与统计学院', '19'),
                            ('计算机工程学院', '20'), ('机械工程学院', '21'), ('经济管理学院', '23'),
                            ('资源环境与旅游学院', '24'), ('汽车与交通工程学院', '25')]
        profession_tuple = [('法学类（法学、社会工作）', 'A179A869B35A46D59B31EB48046C1884', '政法学院'),
                            ('法学', '030101', '政法学院'),
                            ('法学（第二学士学位）', '0ABB340E101845538F86374FB1F164A5', '政法学院'),
                            ('法学(辅修）', 'E26D4BF6BF144D5E9C21A46FAF2D1EFD', '政法学院'),
                            ('社会工作', '030302', '政法学院'),
                            ('社会工作（辅修）', 'B1D0311402864CF6A11A9294B32F74AA', '政法学院'),
                            ('学前教育', '040102', '教育学院'),
                            ('学前教育【专升本】', 'C268C4765D6247A28EFF4D568BBAD94B', '教育学院'),
                            ('教育技术学', '040104', '教育学院'),
                            ('教育技术学（辅修）', '5882E516F90D44A78D2159421481234B', '教育学院'),
                            ('学前教育(f辅修）', 'C347A533E21E4E6BAA52DA30EEC08616', '教育学院'),
                            ('汉语言文学', '050101', '文学与传媒学院'),
                            ('汉语言文学(辅修）', '7BF9BEE3056F44ECAF96AD3462D97111', '文学与传媒学院'),
                            ('广播电视学', '3CA6D83FA39C41D7BF21BC6C9B05FD95', '文学与传媒学院'),
                            ('广播电视学（辅修）', '1D4E8D8342A64DE0A0A165888BFB5AC1', '文学与传媒学院'),
                            ('广播电视编导', 'D69A3CD942CD439D98A6DA4C0DD24C20', '文学与传媒学院'),
                            ('英语', '050201', '外国语学院'),
                            ('英语(辅修）', 'FD0BE0A0A8AC4C37A578DAA60B5B056E', '外国语学院'),
                            ('英语【专升本】', '991620B8148149C28CF125057CD73BA8', '外国语学院'),
                            ('日语', '050207', '外国语学院'), ('音乐学', '050401', '音乐与舞蹈学院'),
                            ('音乐表演', '050403', '音乐与舞蹈学院'),
                            ('舞蹈表演', '80DA5042DA2E48419CCA5A23BC0C969A', '音乐与舞蹈学院'),
                            ('动画', '050418', '美术学院'), ('绘画', 'B8F1A4FF569B4BA29497BB547938A6CF', '美术学院'),
                            ('视觉传达设计', 'F708B50078C44F8BB234469304991736', '美术学院'),
                            ('环境设计', '4610AB5F47D84E5E905119ACF54A7CBE', '美术学院'),
                            ('产品设计', 'F0AD335E6A89401DA923479271F8BE11', '美术学院'),
                            ('设计学类', '5895070169F34240B753BE7126DC7443', '美术学院'),
                            ('物理学', '070201', '物理与电子工程学院'),
                            ('电子信息科学与技术', '071201', '物理与电子工程学院'),
                            ('电子信息工程', '080603', '物理与电子工程学院'),
                            ('通信工程', 'FBFF90BA34664AA4A07FE9EECA177B9A', '物理与电子工程学院'),
                            ('电子信息类', 'D01AE3BB21E9479CAD498E569F3706AF', '物理与电子工程学院'),
                            ('土木工程（辅修）', 'EFB02C700FAB4A3695422B30BFF6FC21', '土木工程与建筑学院'),
                            ('建筑学', '080701', '土木工程与建筑学院'), ('土木工程', '080703', '土木工程与建筑学院'),
                            ('土木类', '613ADA95F6304406A2DC5FE017DD248B', '土木工程与建筑学院'),
                            ('土木工程【专升本】', 'A2229F4B2BF24451B795ECCCCD0B2359', '土木工程与建筑学院'),
                            ('道路桥梁与渡河工程', '9C5CFBC20EE84474940BD57B837F4B95', '土木工程与建筑学院'),
                            ('工程管理', '110104', '土木工程与建筑学院'),
                            ('管理科学与工程类', '40DF791E4DF5445F994F4D980BEBF446', '土木工程与建筑学院'),
                            ('工程管理【专升本】', '4361AAB37BC44DCA8F6491F04CA9E596', '土木工程与建筑学院'),
                            ('工程管理（辅修）', '5AB57C75ECC6492C9ADCCD2ED9F77957', '土木工程与建筑学院'),
                            ('工程造价', 'CE9257DD29D74DF8B82FE9F120DC41FA', '土木工程与建筑学院'),
                            ('化学（专升本）', 'F54DE95B64A4407E981357ADA365A122', '食品科学技术学院·化学工程学院'),
                            ('生物科学（专升本）', 'AC3FD51E16154A57B1D88C2A517BA1BC', '食品科学技术学院·化学工程学院'),
                            ('化学工程与工艺', '081101', '食品科学技术学院·化学工程学院'), (
                                '化学工程与工艺（辅修）', '122A723AAF43421A9A0245D9766B78FC',
                                '食品科学技术学院·化学工程学院'),
                            ('食品科学与工程类', '80A110E261DA4198B299FCE4C0C6722B', '食品科学技术学院·化学工程学院'), (
                                '食品科学与工程(辅修）', '3C22CD0947224872996B521850230D60',
                                '食品科学技术学院·化学工程学院'),
                            ('护理学', '1A5CC789DA1E493C829CD21528826B3A', '医学部'),
                            ('护理学（专升本）', '285D20F92BFA4A8ABB4D99DD25E0A9A5', '医学部'),
                            ('临床医学', '100301', '医学部'),
                            ('医学检验技术', 'FD39E70A079441E1B21937BB9676809A', '医学部'),
                            ('市场营销（创业管理方向）', 'CE2B3C1511D147848ED4D06226BB87F9', '创新创业教育学院'),
                            ('体育学类', '2FA11B61E1BC4F23B0D616DB6F5D85F3', '体育学院'),
                            ('体育教育', '040201', '体育学院'), ('社会体育', '040203', '体育学院'),
                            ('社会体育指导与管理', '1760B949DA0F405F9A7061F22A7960EE', '体育学院'),
                            ('数学与应用数学', '070101', '数学与统计学院'),
                            ('数学类', '5647CBA72FAC4E6586912B8985F04305', '数学与统计学院'),
                            ('数学与应用数学（辅修）', 'B99E3D21B87C4947B267FA87C0550FB9', '数学与统计学院'),
                            ('信息与计算科学', '070102', '数学与统计学院'),
                            ('信息与计算科学（辅修）', 'B966814DAE5B43A0A251931B02D136E8', '数学与统计学院'),
                            ('数据计算及应用', '8FCE0B115B144B7BA8351C79B7EDCC7A', '数学与统计学院'),
                            ('计算机科学与技术', '080605', '计算机工程学院'),
                            ('计算机科学与技术【专升本】', '28485E828F5D4F389B98CE467AE505D2', '计算机工程学院'),
                            ('软件工程', '080611', '计算机工程学院'),
                            ('计算机科学与技术（辅修）', 'C8DD16C3C77A4D26A9E6C25C91F12167', '计算机工程学院'),
                            ('物联网工程', '6FD36D5F1FEB4AB3BF08848F0FDECB75', '计算机工程学院'),
                            ('计算机类', '3EF3F3DC1D654C1CBB268FC572F8E642', '计算机工程学院'),
                            ('机械类', '623F618281A0475D8AFC2F8CFB69A108', '机械工程学院'),
                            ('机械设计制造及其自动化（辅修）', '39DAB72A83BB4557A2765DBE123D2189', '机械工程学院'),
                            ('智能制造工程', 'CFA5EBFD963E47D38781926257F4808F', '机械工程学院'),
                            ('机械设计制造及其自动化', '080301', '机械工程学院'),
                            ('机械设计制造及其自动化【专升本】', '0106BC205E37497D8156568B0EA8A661', '机械工程学院'),
                            ('工业工程', '110103', '机械工程学院'),
                            ('工业工程（辅修）', '8CB1CE2FE4084C9FA756F25E97DCDC03', '机械工程学院'),
                            ('国际经济与贸易', '020102', '经济管理学院'),
                            ('国际经济与贸易【专升本】', 'EE778815EA38437181786A9A8C603B72', '经济管理学院'),
                            ('国际经济与贸易（辅修）', 'BF447082B3064765A81C43DF0741EFCE', '经济管理学院'),
                            ('市场营销', '110202', '经济管理学院'),
                            ('工商管理类', 'C10125AFF7664348BC6FE7C273162911', '经济管理学院'),
                            ('市场营销【专升本】', 'D2620B26229E478F99333FEEC0FCD80A', '经济管理学院'),
                            ('物流管理', '110210W', '经济管理学院'),
                            ('市场营销（辅修）', 'F24F8ECFCCC2499C836228787BB9AC30', '经济管理学院'),
                            ('财务管理', '80C314F1B04A494AA545E63F068EE576', '经济管理学院'),
                            ('财务管理（专升本）', '6B287D02CDD64DF4B6D0B1BFE58FEC5E', '经济管理学院'),
                            ('工商企业管理', '620501', '经济管理学院'),
                            ('地理科学（辅修）', 'FAE5B2DCC3394E7FB6B4A99F1668B615', '资源环境与旅游学院'),
                            ('地理科学', '070701', '资源环境与旅游学院'),
                            ('地理科学（专升本）', '9DB5D30497AC4B0681B8B59E916EE085', '资源环境与旅游学院'),
                            ('旅游管理(本)', '110206', '资源环境与旅游学院'),
                            ('旅游管理【专升本】', 'B36AE8621F7A4BFA84E5A46F77A4DA7C', '资源环境与旅游学院'),
                            ('旅游管理(辅修）', '2E1A0A6B944F410FB49195BB32F38122', '资源环境与旅游学院'),
                            ('车辆工程(辅修）', 'BCBF886613E54457BA3911608228110F', '汽车与交通工程学院'),
                            ('汽车服务工程（专升本）', '80BE01BC658646529822366D43477900', '汽车与交通工程学院'),
                            ('车辆工程', '080306W', '汽车与交通工程学院'), ('自动化', '080602', '汽车与交通工程学院'),
                            ('交通设备与控制工程', 'C95AC2FB20334B909735A744B7416029', '汽车与交通工程学院')]

        url = self.base_url + 'kbcx/kbxx_xzb_ifr'
        data = {
            'xnxqh': semester,
            'skyx': department,
            'sknj': grade,
            'skzy': profession,
            'zc1': week_start,
            'zc2': week_end,
            'jc1': lesson_start,
            'jc2': lesson_end,
        }
        response = self.session.post(url, headers=self.headers, data=data)
        assert response.status_code == 200, 'Failed to get class schedule'
        return response.content

    def get_lesson_score(self, semester: str, types: str = '', score: str = 'all') -> bytes:
        select = {
            '': '',
            '公共课': '01',
            '公共基础课': '02',
            '专业基础课': '03',
            '专业课': '04',
            '专业选修课': '05',
            '公共选修课': '06',
            '通识教育必修': '07',
            '学科基础课': '08',
            '专业核心课': '09',
            '方向必修课': '10',
            '方向选修课': '11',
            '通识教育选修': '12',
            '其他': '13',
            '专业方向课': '14',
            '专业必修课': '15',
            '创新创业课': '16',
        }
        """
        [('', ''), ('公共课', '01'), ('公共基础课', '02'), ('专业基础课', '03'), ('专业课', '04'),
                  ('专业选修课', '05'), ('公共选修课', '06'), ('通识教育必修', '07'), ('学科基础课', '08'),
                  ('专业核心课', '09'), ('方向必修课', '10'), ('方向选修课', '11'), ('通识教育选修', '12'),
                  ('其他', '13'), ('专业方向课', '14'), ('专业必修课', '15'), ('创新创业课', '16')]
                  """
        url = self.base_url + 'kscj/cjcx_list'
        data = {'kksj': semester, 'kcxz': select[types], 'kcmc': '', 'xsfs': score}
        response = self.session.get(url, headers=self.headers, params=data)
        assert response.status_code == 200, 'Failed to get lesson score'
        return response.content

    def login(self, **kwargs) -> httpx.Response:
        response = self.post_login(**kwargs)
        if response.url.path != '/jsxsd/framework/xsMain.jsp':
            raise Exception('Wrong username or password')
        self.is_login = True
        return response


if __name__ == "__main__":
    self = Request()
    print(self.login())
    print(self.get_class_schedule('2023-2024-1', '20', '2022', '080605'))
