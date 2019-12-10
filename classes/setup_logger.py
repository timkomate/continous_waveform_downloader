import logging
from datetime import datetime
import os

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H:%M:%S")

if (not os.path.exists("./logs")):
    os.mkdir("./logs")

log_format = "%(asctime)s::%(levelname)s::%(filename)s::%(lineno)d::%(message)s"
logging.basicConfig(
    filename='./logs/%s.log' % (dt_string), 
    level='DEBUG', 
    format=log_format
)

logger = logging.getLogger("data-download")