import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import get_folder_path


# Remove default output
logger.remove()


# Log format
fmt: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{message}</level>"

# Log level
level: int = SETTINGS["log.level"]

# Add console output
if SETTINGS["log.console"]:
    logger.add(sys.stdout, colorize=True, format=fmt, level=level)

# Add file output
if SETTINGS["log.file"]:
    today_date: str = datetime.now().strftime("%Y%m%d")
    filename: str = f"alpha_{today_date}.log"
    log_path: Path = get_folder_path("log")
    file_path: Path = log_path.joinpath(filename)

    logger.add(sink=file_path, format=fmt, level=level)
