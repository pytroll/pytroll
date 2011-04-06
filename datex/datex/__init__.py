import sys
import logging

datetime_format = '%Y-%m-%dT%H:%M:%S.%f' 

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, datefmt="%Y-%m-%d %H:%M:%S", 
                    level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger('datex')

from datex.config import DatexConfig 
datex_config = DatexConfig()
