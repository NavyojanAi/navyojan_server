
import logging
from pathlib import Path
import os

debug_file_path = Path(__file__).resolve().parent
os.makedirs(debug_file_path, exist_ok=True)

logger = logging.getLogger("navyojan_logger")
logger.setLevel(logging.DEBUG)
# add multiple handlers
# sh = logging.StreamHandler(sys.stdout)
# sh.setLevel(logging.INFO)
fh1 = logging.FileHandler(debug_file_path / 'log_info.log', mode='w+')
fh1.setLevel(logging.INFO)

fh2 = logging.FileHandler(debug_file_path / 'log_debug.log', mode='w+')
fh2.setLevel(logging.DEBUG)
# formatter
formater = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')
fh1.setFormatter(formater)
fh2.setFormatter(formater)

logger.addHandler(fh1)
logger.addHandler(fh2)