# -*- coding: utf-8 -*-

import logging
import os.path
import sqlite3

INSTAGRAM_ALBUM = """
CREATE TABLE `album` (
  `shortcode` varchar(64) NOT NULL,
  `owner` varchar(64),
  `media_count` tinyint(3) NOT NULL DEFAULT '0',
  `ct` datetime NOT NULL,
  PRIMARY KEY (`shortcode`)
)
"""

INSTAGRAM_MEDIA = """
CREATE TABLE `media` (
  `id` varchar(64) NOT NULL,
  `album_shortcode` varchar(64) NOT NULL,
  `is_video` char(1) NOT NULL DEFAULT 'N',
  `image_url` varchar(1024) NOT NULL,
  `video_url` varchar(1024),
  `tagusers` varchar(1024),
  `download_flag` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`)
)
"""

log = logging.getLogger('refusea.lib.db')


# 单例使用
class DbHelper(object):

    def __init__(self):
        db_file = DbHelper.prepare_database()
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

    def select(self, sql, params=None):
        """执行查询语句， 返回一个记录集"""
        cursor = self.conn.cursor()
        try:
            count = cursor.execute(
                sql, params) if params else cursor.execute(sql)
            return cursor.fetchall() if count else None
        except Exception as ex:
            log.error('db error: sql=%s, ex=%s', sql, ex, stack_info=True)
            return None
        finally:
            cursor.close()

    def execute(self, sql, args=None) -> int:
        """执行更新操作， 返回影响的行数"""
        cursor = self.conn.cursor()
        try:
            result = cursor.execute(sql, args)
            if result:
                self.conn.commit()
            return result
        except Exception as ex:
            log.error('db error: sql=%s, ex=%s', sql, ex, stack_info=True)
            return 0
        finally:
            cursor.close()

    @staticmethod
    def prepare_database() -> str:
        root_path = os.path.dirname(os.path.dirname(__file__))
        db_file = os.path.join(root_path, 'instagram.db')

        if not os.path.exists(db_file):

            log.debug('initiate database in %s', db_file)

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            try:
                cursor.execute(INSTAGRAM_ALBUM)
                cursor.execute(INSTAGRAM_MEDIA)
                cursor.close()
                conn.commit()
            except Exception as ex:
                log.error('prepare database error, ex=%s', ex, stack_info=True)
            finally:
                cursor.close()
                conn.close()

        return db_file


dbh = DbHelper()
