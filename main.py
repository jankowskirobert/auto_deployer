import logging

from src.flow import execute_flow
from src.sys_utils import setup_basic_logger
import configparser
logger = logging.getLogger("main")

if __name__ == '__main__':
    cfg = configparser.RawConfigParser()
    cfg.read('app.cfg')
    par = dict(cfg.items("Settings"))
    print(par)
    setup_basic_logger()
    #
    execute_flow()