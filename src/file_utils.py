import logging
import shutil

logger = logging.getLogger("main")

def create_lambdas_file_zip(lambdas_directory: str, output_filename, file_format: str) -> bool:
    try:
        shutil.make_archive(output_filename, file_format,lambdas_directory)
        logger.info('Archive has been successfully Created')
        return True
    except Exception as exp:
        logger.error('Could not Create ZIP File')
        return False