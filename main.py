import logging

from src.flow import execute_flow
from src.sys_utils import setup_basic_logger
import configparser

logger = logging.getLogger("main")

if __name__ == '__main__':
    cfg = configparser.RawConfigParser()
    cfg.read('app.cfg')
    par = dict(cfg.items("Settings"))
    logger.info('Loaded Setting from file %s', par)
    region = par['aws_region']
    pem_bucket_name = par['pem_bucket_name']
    lambda_bucket_name = par['lambda_bucket_name']
    root_api_path = par['root_api_path']
    setup_basic_logger()
    #
    execute_flow(region,
                 'test-1-5',
                 lambda_bucket_name,
                 pem_bucket_name,
                 root_api_path)
    logger.info("IaC tool finished working")