from pathlib import Path
from typing import Literal

LogLevel = Literal['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']

# Zotero 本地 API 端点
ENDPOINT: str = 'http://localhost:23124/api'

# 日志名称
LOGGER_NAME: str = 'ZoteroMCP'
# 日志文件夹
LOG_DIR: Path = Path.cwd() / 'logs'
# 日志文件名
LOG_FILE: str = 'zotero_mcp.log'
# 文件输出日志级别
LOG_LEVEL_FILE: LogLevel = 'INFO'
# 标准输出日志级别
LOG_LEVEL_STDOUT: LogLevel = 'DEBUG'
