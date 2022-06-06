import logging
import logging.handlers
from utils.settings import settings
from concurrent_log_handler import ConcurrentRotatingFileHandler

logger = logging.getLogger(settings.app_name)
logger.setLevel(logging.INFO)
log_handler = ConcurrentRotatingFileHandler(
    f"{settings.log_path}/x-ljson.log", "a", 5_000_000, 10
)
#log_handler = logging.handlers.RotatingFileHandler(
#    filename=settings.log_path / settings.log_filename, maxBytes=5000000, backupCount=10
#)
logger.addHandler(log_handler)
