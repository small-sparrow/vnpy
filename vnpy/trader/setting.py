"""
Global setting of the trading platform.
"""

from logging import INFO
from tzlocal import get_localzone_name

from .utility import load_json


SETTINGS: dict = {
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": INFO,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "",
    "datafeed.username": "",
    "datafeed.password": "",

    "database.timezone": get_localzone_name(),
    "database.name": "postgresql",
    "database.database": "vnpy",
    "database.host": "127.0.0.1",
    "database.port": 5432,
    "database.user": "vnpy",
    "database.password": "3e*@%dr12"
}


# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))
