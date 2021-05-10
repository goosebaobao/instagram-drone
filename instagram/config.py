# -*- coding: utf-8 -*-

USERNAME = 'your username'
PASSWORD = 'your password'
# {unxi 时间戳}
ENC_PASSWORD = '#PWD_INSTAGRAM_BROWSER:0:{}:' + PASSWORD

# QUERY_HASH = 'd4d88dc1500312af6f937f7b804c68c3'
# QUERY_HASH = 'f883d95537fbcd400f466f63d42bd8a1'
# QUERY_HASH = '2ce1d673055b99250e93b6f88f878fde'

# firefox
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'

# chrome
# USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#               'AppleWebKit/537.36 (KHTML, like Gecko) '
#               'Chrome/90.0.4430.72 Safari/537.36')

# iOS
USER_AGENT = ('Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) '
              'AppleWebKit/605.1.15 (KHTML, like Gecko) '
              'Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN')


HEADERS = {'user-agent': USER_AGENT}

# 首页
HOME_URL = 'https://www.instagram.com'
# 登录页
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'

# 获取收藏的起始页 {username}
GRAPHQL_START_URL = 'https://www.instagram.com/{}/?__a=1'.format(USERNAME)
# 获取收藏的后续页 {user_id} {page_size} {end_cursor}
GRAPHQL_NEXT_URL = ('https://www.instagram.com/graphql/query/?query_hash=2ce1d673055b99250e93b6f88f878fde'
                    '&variables={{"id":"{}","first":{},"after":"{}"}}')
# 收藏详情页 json {shortcode}
GRAPHQL_SHORTCODE_URL = ('https://www.instagram.com/graphql/query/?query_hash=d4e8ae69cb68f66329dcebe82fb69f6d'
                         '&variables={{"shortcode":"{}"}}')
# 每页获取几个收藏? 默认 12
GRAPHQL_PAGE_SIZE = 50

# 是否爬取整个收藏, 若设为 False, 当一页的数据全部已爬取时会返回
FULL_CRAWLING = False
