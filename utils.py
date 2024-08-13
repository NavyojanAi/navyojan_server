import logging
import sys
from pathlib import Path
import os

debug_file_path = Path(__file__).resolve().parent / "logs"
os.makedirs(debug_file_path, exist_ok=True)

logger = logging.getLogger("default")

def setup_logger(logger, filename_base):
    logger.setLevel(logging.DEBUG)
    fh1 = logging.FileHandler(debug_file_path / f"{filename_base}_info.log", mode="a")
    fh1.setLevel(logging.INFO)

    fh2 = logging.FileHandler(debug_file_path / f"{filename_base}_debug.log", mode="a")
    fh2.setLevel(logging.DEBUG)
    
    # formatter
    formater = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s"
    )
    fh1.setFormatter(formater)
    fh2.setFormatter(formater)

    logger.addHandler(fh1)
    logger.addHandler(fh2)
    
setup_logger(logger, "backend")
