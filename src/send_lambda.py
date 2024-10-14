#arn:aws:iam::927409320646:role/lambda-execution-manual
import shutil
import boto3

s3Resource = boto3.resource('s3')
s3_client = boto3.client('s3')

path_to_dir = './lambda_functions'

output_filename = 'my-zip'

shutil.make_archive(output_filename, 'zip', path_to_dir)

print('Zip archive of directory created.')
try:
    s3Resource.meta.client.upload_file(
        'my-zip.zip',
        'robertjankowski-lambdas',
        'test-key')

except Exception as exp:
    print('exp: ', exp)
