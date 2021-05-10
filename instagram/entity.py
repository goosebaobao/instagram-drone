# -*- coding: utf-8 -*-

from typing import List, Dict, Any

from instagram.config import FULL_CRAWLING


class Album(object):
    """collection of media"""

    def __init__(self) -> None:
        self.shortcode: str = None
        self.owner: str = None
        self.media_count: int = 0

    @classmethod
    def from_record(cls, record: tuple) -> "Album":
        album = cls()
        album.shortcode = record[0]
        album.owner = record[1]
        album.media_count = record[2]
        return album

    @classmethod
    def from_json_node(cls, node: dict) -> "Album":
        album = cls()
        album.shortcode = node['shortcode']
        return album

    def __repr__(self) -> str:
        return 'Album: shortcode={}'.format(self.shortcode)


class Media(object):
    """媒体信息, 图片或视频"""

    def __init__(self) -> None:
        self.album_shortcode: str = None
        self.id: str = None
        self.is_video: str = 'N'
        self.image_url: str = None
        self.video_url: str = None
        self.tagusers: str = None
        self.download_flag: str = 'N'

        self.owner: str = None

    @classmethod
    def from_json_node(cls, album_shortcode: str, node: Dict[str, Any]) -> "Media":
        media = cls()
        media.album_shortcode = album_shortcode

        media.id = node['id']
        media.image_url = node["display_url"]

        is_video = node['is_video']
        media.is_video = 'Y' if is_video else 'N'
        media.video_url = node['video_url'] if is_video else None

        taguser_list: List[str] = []
        edge_media_to_tagged_user = node.get('edge_media_to_tagged_user')
        if edge_media_to_tagged_user:
            edges = edge_media_to_tagged_user.get('edges')
            if edges:
                for item in edges:
                    taguser_list.append(item['node']['user']['username'])
        if taguser_list:
            media.tagusers = ','.join(taguser_list)

        return media

    @classmethod
    def from_record(cls, record: tuple) -> "Media":
        media = cls()
        media.id = record[0]
        media.album_shortcode = record[1]
        media.is_video = record[2]
        media.image_url = record[3]
        media.video_url = record[4]
        media.tagusers = record[5]
        media.download_flag = record[6]

        return media

    @classmethod
    def from_record2(cls, record: tuple) -> "Media":
        media = cls()
        media.id = record[0]
        media.album_shortcode = record[1]
        media.owner = record[2]
        media.is_video = record[3]

        return media

    def __repr__(self):
        return 'Media: id={}, url={}'.format(self.id, self.image_url)


class InstagramSession(object):
    """爬虫的会话信息"""

    def __init__(self) -> None:
        self.user_id = 0
        self.page_num = 1
        # 是否还有下一页数据
        self.has_next_page: bool = False
        # 游标
        self.end_cursor: str = None
        # 最后爬取的一页 album
        self.last_page: List[Album] = None
        # 爬取到的新 album 数量
        self.fresh_count = 0

        self.albums: Dict[str, Album] = {}

    def merge(self) -> bool:
        """将新爬回的 album 合入到 album 列表, 并返回是否有新 album"""
        if not self.last_page:
            return False

        fresh = False
        for album in self.last_page:
            if album.shortcode not in self.albums:
                self.albums[album.shortcode] = album
                self.fresh_count += 1
                fresh = True

        return fresh or FULL_CRAWLING
