from loguru import logger

# 添加日志记录
logger.add("log/info.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='INFO', rotation="10 MB",
           encoding='utf-8')
logger.add("log/error.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='ERROR',
           rotation="10 MB", encoding='utf-8')
logger.add("log/debug.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='DEBUG',
           rotation="10 MB", encoding='utf-8')
