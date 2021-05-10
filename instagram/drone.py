# -*- coding: utf-8 -*-

import json
import logging
import os
import os.path
import random
import time

from typing import Any, List, Dict


from lib.http_helper import HttpHelper

from instagram.entity import Album, Media, InstagramSession
from instagram.dao import dao
from instagram.config import (USERNAME, ENC_PASSWORD, HEADERS,
                              HOME_URL, LOGIN_URL,  GRAPHQL_SHORTCODE_URL,
                              GRAPHQL_NEXT_URL, GRAPHQL_START_URL, GRAPHQL_PAGE_SIZE)


log = logging.getLogger('refusea.instagram.drone')

http = HttpHelper(headers=HEADERS)
session = InstagramSession()

root_path = os.path.dirname(os.path.dirname(__file__))
media_path = os.path.join(root_path, 'static', 'instagram')


def login() -> None:
    """使用帐号密码登录, 登录成功获得 user_id"""

    http.get(HOME_URL)

    http.update_headers({'X-CSRFToken': http.get_cookie('csrftoken')})

    data = {'username': USERNAME,
            'enc_password': ENC_PASSWORD.format(int(time.time()))}
    result = http.post(LOGIN_URL, data=data, allow_redirects=False)

    if result:
        ret = json.loads(result)
        if "ok" == ret['status'] and ret['authenticated']:
            session.user_id = ret['userId']


def graphql_start_page() -> None:
    """ajax 访问收藏首页, 解析出收藏内容"""
    result = http.get(GRAPHQL_START_URL, allow_redirects=False)
    if result:
        ret = json.loads(result)
        extract_album(ret['graphql']['user'])


def graphql_next_page() -> None:
    """ajax 访问收藏下一页, 从 js 脚本解析出收藏内容"""

    session.page_num += 1

    url = GRAPHQL_NEXT_URL.format(
        session.user_id, GRAPHQL_PAGE_SIZE, session.end_cursor)
    result = http.get(url, allow_redirects=False)
    if result:
        ret = json.loads(result)
        extract_album(ret['data']['user'])
    else:
        session.has_next_page = False


def extract_album(user: Dict[str, Any], ) -> None:
    """从收藏页返回的 json user 节点解析出 album; 并获取是否有下页, 及下页的游标"""

    edge_saved_media = user["edge_saved_media"]

    page_info = edge_saved_media["page_info"]
    session.has_next_page = page_info["has_next_page"]
    session.end_cursor = page_info["end_cursor"]

    edges = edge_saved_media["edges"]
    session.last_page = [Album.from_json_node(edge["node"]) for edge in edges]


def graphql_shortcode(album: Album) -> List[Media]:
    """ ajax 调用, 获取详情, 解析出媒体信息"""

    url = GRAPHQL_SHORTCODE_URL.format(album.shortcode)
    result = http.get(url, allow_redirects=False)

    if not result:
        return None

    ret = json.loads(result)
    shortcode_media = ret['data']['shortcode_media']
    return resolve_media(album, shortcode_media)


def resolve_media(album: Album, shortcode_media: Dict[str, Any]) -> List[Media]:
    """从 json 解析出媒体信息"""

    if not album.owner:
        album.owner = shortcode_media["owner"]["username"]

    medias = []
    if shortcode_media["__typename"] == "GraphSidecar":
        edges = shortcode_media["edge_sidecar_to_children"]["edges"]
        for edge in edges:
            medias.append(Media.from_json_node(album.shortcode, edge['node']))
    else:
        medias.append(Media.from_json_node(album.shortcode, shortcode_media))

    return medias


def crawling() -> None:
    """从 instagram.com 爬取收藏的媒体"""

    # 登录
    login()
    log.debug('user_id: %s', session.user_id)

    if not session.user_id:
        # login fail
        return

    sleep()

    # 从 db 加载所有 album
    load_albums_for_session()

    log.debug('get albums from your favorite')

    # 获取收藏首页
    graphql_start_page()
    log.debug('>> page %s, album count: %s',
              session.page_num, len(session.last_page))

    while session.merge() and session.has_next_page:

        sleep()

        # 获取收藏下一页, 直到最后一页或当前页的所有数据都已获取过
        graphql_next_page()
        log.debug('>> page %s, album count: %s', session.page_num,
                  len(session.last_page))

        # 每 10 页, 额外休眠一次
        if session.page_num % 10 == 0:
            sleep()

    log.debug(">> fresh album count: %s", session.fresh_count)

    if session.fresh_count:
        log.debug('>> save fresh albums to db')
        dao.insert_albums(session.albums.values())

    log.debug('get medias for every album')

    n = 0
    total = len(session.albums)
    for album in session.albums.values():
        n += 1
        if album.media_count > 0:
            continue

        log.debug('>> %s: %s of %s', album.shortcode, n, total)

        sleep()

        log.debug('>>>> get medias')

        medias = graphql_shortcode(album)
        if not medias:
            log.debug(
                '!! WARNING !! '
                '429 Too Many Requests, try longer interval...')
            sleep(60, 90)
            continue

        log.debug('>>>>>> media count: %s', len(medias))
        dao.save_medias(album, medias)

        # 额外休眠一次
        if n % 15 == 0:
            sleep(5, 10)


def download_media():
    """下载媒体"""

    log.debug('download media from instagram.com')

    if not os.path.exists(media_path):
        os.mkdir(media_path)

    medias = dao.list_medias(download_flag='N')
    if not medias:
        log.debug('all media downloaded. exit...')
        return

    err_count = 0
    save_count = 0
    count = 0
    total = len(medias)

    for media in medias:

        count += 1
        mid = media.id

        log.debug('>> %s: %s of %s', mid, count, total)

        result = save_to_disk(mid, media.image_url, '.jpeg') and save_to_disk(
            media.id, media.video_url, '.mp4')

        if result:
            save_count += 1
            dao.mark_downloaded(mid)
        else:
            err_count += 1

    log.debug('download done. total: %s, save: %s, error: %s',
              total, save_count, err_count)


def save_to_disk(id: str, url: str, ext: str = '.jpeg') -> None:

    if not url:
        return True

    filename = os.path.join(media_path, id + ext)
    if os.path.exists(filename):
        return True

    try:
        content = http.download(url)
        if content:
            with open(filename, "wb") as file:
                file.write(content)
            log.debug('>>>> %s%s saved', id, ext)
            return True
    except Exception as ex:
        log.error('save media to disk fail: %s%s, err=%s',
                  id, ext, ex, stack_info=True)

    return False


def sleep(min=1, max=4) -> None:
    """随机休眠 1~~4 秒钟"""
    n = random.randint(min, max)
    log.debug('>> sleep %s seconds...', n)
    time.sleep(n)


def load_albums_for_session() -> None:
    album_list = dao.list_albums()
    if album_list:
        album_dict = {album.shortcode: album for album in album_list}
        session.albums = album_dict
