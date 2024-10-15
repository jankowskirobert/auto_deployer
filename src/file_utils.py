import logging
import os
import shutil

logger = logging.getLogger("main")
import zipfile


# Create a new zip file

def zip_directory(folder_path, zip_file):
    os_walk = os.walk(folder_path)
    print(os_walk)
    for folder_name, subfolders, filenames in os_walk:
        print(filenames)
        print(subfolders)
        print(folder_name)
        for filename in filenames:
            # Create complete filepath of file in directory
            file_path = os.path.join(folder_name, filename)
            # Add file to zip
            zip_file.write(file_path)


def create_lambdas_file_zip(lambdas_directory: str, output_filename, file_format: str) -> bool:
    try:
        shutil.make_archive(output_filename, file_format,lambdas_directory)
        logger.info('Archive has been successfully Created')
        return True
    except Exception as exp:
        logger.error('Could not Create ZIP File')
        return False
    # zip_file = zipfile.ZipFile(output_filename + '.zip', 'w')
    #
    # # Add a file to the zip file
    # zip_directory(lambdas_directory, zip_file)
    #
    # # Close the zip file
    # zip_file.close()
    # return True