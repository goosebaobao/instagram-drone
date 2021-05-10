# -*- coding: utf-8 -*-

from typing import List

from instagram.entity import Album, Media
from lib.db_helper import dbh

import logging

log = logging.getLogger('refusea.instagram.dao')

LIMIT = 6


class __InstagramDao(object):

    @staticmethod
    def list_albums() -> List[Album]:
        sql = ("select shortcode, owner, media_count from album")
        result = dbh.select(sql)
        return [Album.from_record(record) for record in result] if result else None

    @staticmethod
    def insert_albums(albums: List[Album]) -> None:
        if not albums:
            return

        sql = "insert into album (shortcode, owner, media_count, ct) values (?, null, 0, datetime('now'))"
        for album in albums:
            if album.media_count == 0:
                dbh.execute(sql, (album.shortcode, ))

    @staticmethod
    def list_medias(download_flag: str = None) -> List[Media]:
        sql = ("select "
               "id, album_shortcode, is_video, image_url, video_url, tagusers, download_flag "
               "from media")
        if download_flag:
            sql += " where download_flag='" + download_flag + "'"
        result = dbh.select(sql)
        return [Media.from_record(record) for record in result] if result else None

    @staticmethod
    def save_medias(album: Album, medias: List[Media]) -> None:
        if not medias:
            return

        sql = ("insert into media "
               "(id, album_shortcode, is_video, image_url, video_url, tagusers, download_flag) values "
               "(?, ?, ?, ?, ?, ?, 'N')")
        for media in medias:
            dbh.execute(sql, (media.id, media.album_shortcode,
                              media.is_video, media.image_url, media.video_url, media.tagusers))

        count = len(medias)
        sql = "update album set media_count=?, owner=? where shortcode=?"
        result = dbh.execute(sql, (count, album.owner, album.shortcode,))
        if result:
            album.media_count = count

    @staticmethod
    def search_medias(id: str = None, owner: str = None, tag: str = None, page: int = 1) -> List[Media]:
        if page < 1:
            page = 1

        sql = ("SELECT m.id, m.album_shortcode, a.owner, m.is_video FROM media m, album a "
               "WHERE m.album_shortcode=a.shortcode AND m.download_flag='Y'")
        if id:
            sql += " AND m.id='" + id + "'"
        if owner:
            sql += " AND a.owner='" + owner + "'"
        if tag:
            sql += " AND m.tagusers like '%" + tag + "%'"
        sql += " order by m.id desc limit "
        sql += str((page - 1) * LIMIT) + ", " + str(LIMIT)

        result = dbh.select(sql)
        return [Media.from_record2(record) for record in result] if result else None

    @staticmethod
    def mark_downloaded(id: str):
        sql = "update media set download_flag='Y' where id=?"
        return dbh.execute(sql, (id,))

    @staticmethod
    def list_onwers() -> List[str]:
        sql = 'select distinct owner from album where owner is not null'
        result = dbh.select(sql)
        owners = [record[0] for record in result] if result else []
        if owners:
            owners.sort()
        return owners


dao = __InstagramDao()
