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

    def login(self, username: str = config.account.get('username'),
              password: str = config.account.get('password')) -> httpx.Response:
        username_encoded = self.encode(username)
        password_encoded = self.encode(password)
        encoded = username_encoded + '%%%' + password_encoded

        return self.session.post(self.base_url + 'xk/LoginToXk', headers=self.headers, data={'encoded': encoded})

    def post_schedule(self, semester: str) -> httpx.Response:
        return self.session.post(self.base_url + 'xskb/xskb_print.do',
                                 headers=self.headers, data={'xnxq01id': semester, 'zc': ''})

    


if __name__ == "__main__":
    self = Request()
    print(self.login())
