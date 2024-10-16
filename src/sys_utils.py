import configparser
import logging
import sys

logger = logging.getLogger('main')
logger_root = logging.getLogger('root')


def setup_basic_logger():
    logging.basicConfig(filename='setuper.log', level=logging.DEBUG)
    file_handler = logging.FileHandler(filename='root.log')
    logger_root.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger_root.addHandler(file_handler)

def load_config() -> dict:
    cfg = configparser.RawConfigParser()
    cfg.read('app.cfg')
    return dict(cfg.items("Settings"))