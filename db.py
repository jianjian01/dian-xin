import random
from datetime import datetime

from pony.orm import Database, Required, set_sql_debug, PrimaryKey, Optional, Set, select, LongStr

from config import Config

db = Database()

set_sql_debug(True)


class UserStatus:
    delete = -1
    not_exist = 0
    normal = 1


class UserSource:
    github = 1
    weibo = 2
    google = 3


class User(db.Entity):
    """用户"""
    id = PrimaryKey(int, auto=True)
    u_id = Required(int, unique=True, py_check=lambda x: User.id_min < x < User.id_max)
    name = Required(str)
    avatar_url = Optional(str)
    source = Required(int)
    source_id = Required(str)
    source_data = Optional(LongStr)

    sites = Set(lambda: UserSite)
    categories = Set(lambda: Category)
    user_rss = Set(lambda: UserRSS)

    status = Required(int, default=UserStatus.normal)
    create_time = Required(datetime, default=datetime.utcnow)
    last_login_time = Required(datetime, default=datetime.utcnow)

    # 生成自定义 ID
    id_min = 100000000
    id_max = 999999999

    @staticmethod
    def new_uid():
        """生成新的用户ID"""
        while 1:
            n_id = random.randint(User.id_min, User.id_max)
            if not User.select(lambda c: c.u_id == n_id):
                return n_id


class Site(db.Entity):
    """网站信息"""
    id = PrimaryKey(int, auto=True)
    host = Required(str, unique=True, index=True)
    icon = Optional(str)


class Category(db.Entity):
    """分类"""
    id = PrimaryKey(int, auto=True)
    name = Required(str, index=True)
    user = Required(User)
    order = Required(int, default=20)
    hide = Required(bool, default=False)
    delete = Required(bool, default=False)
    sites = Set(lambda: UserSite)


class UserSiteStatus:
    normal = 1
    delete = 0


class UserSite(db.Entity):
    """用户保存网站信息"""
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    url = Required(str)
    icon = Optional(str)
    user = Required(User)
    cate = Optional(Category)
    order = Required(int, default=20)
    create_time = Required(datetime, default=datetime.utcnow)
    status = Required(int, default=UserSiteStatus.normal)
    delete_time = Optional(datetime)


class RSS(db.Entity):
    """rss 订阅信息"""
    id = PrimaryKey(int, auto=True)
    name = Required(str, nullable=True)
    link = Required(str, unique=True)
    page = Set(lambda: Page)
    user_rss = Set(lambda: UserRSS)
    mark = Required(bool, default=False)


class Page(db.Entity):
    """rss 获取到的信息"""
    page_id = Required(str)
    title = Required(str)
    link = Required(str)
    publish_date = Optional(datetime)
    rss = Required(RSS)

    PrimaryKey(page_id, rss)


class UserRSS(db.Entity):
    """用户信息"""
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    user = Required(User)
    rss = Required(RSS)

    create_time = Required(datetime, default=datetime.utcnow)
    delete = Required(bool, default=False)
    delete_time = Optional(datetime)


if __name__ == '__main__':
    db.bind(**Config.PONY)
    db.generate_mapping(create_tables=True)
