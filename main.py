import boto3

# Let's use Amazon S3
s3 = boto3.client('s3')

def print_hi(name):
    paginator = s3.get_paginator('list_objects')
    result = paginator.paginate(Bucket='init0', Delimiter='/')
    for prefix in result.search('CommonPrefixes'):
        print(prefix.get('Prefix'))
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
