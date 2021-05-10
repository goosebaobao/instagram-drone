# -*- coding: utf-8 -*-
import logging
import requests


# 超时设置 (连接超时, 读超时) 秒
TIMEOUT = (10, 60)

# 代理服务器
PROXIES = None
PROXIES = {"http": "http://127.0.0.1:31080", "https": "http://127.0.0.1:31080"}

ENCODING = 'utf-8'

log = logging.getLogger('refusea.lib.http')


class HttpHelper(object):

    def __init__(self, encoding=ENCODING, timeout=TIMEOUT, proxies=PROXIES, headers=None):
        self.encoding = encoding
        self.timeout = timeout

        session = requests.session()
        if proxies:
            session.proxies = proxies
        if headers:
            session.headers.update(headers)
        self.session = session

    def get(self, url, **kwargs) -> str:
        rsp = self.request('GET', url, **kwargs)
        return rsp.text if rsp else None

    def post(self, url, **kwargs) -> str:
        rsp = self.request('POST', url, **kwargs)
        return rsp.text if rsp else None

    def download(self, url, **kwargs) -> bytes:
        """下载, 返回字节数组"""
        rsp = self.request('GET', url, **kwargs)
        return rsp.content if rsp else None

    def request(self, method, url,  **kwargs):

        # 确保 timeout 被设置
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            rsp = self.session.request(method, url, **kwargs)
        except Exception as ex:
            log.error('http %s error. url=%s, args=%s, ex=%s',
                      method, url, kwargs, ex, stack_info=True)
            return None

        if rsp.status_code >= 300 or rsp.status_code < 200:
            log.warning('http %s fail. url=%s, args=%s, status=%s, text=%s',
                        method, url, kwargs, rsp.status_code, rsp.text)
            return None

        rsp.encoding = self.encoding

        return rsp

    def get_cookie(self, key):
        """获取 cookie 值"""
        return self.session.cookies.get(key)

    def update_headers(self, headers):
        self.session.headers.update(headers)
