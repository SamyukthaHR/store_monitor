import boto3

from utils.constants import BUCKET_NAME, S3_URL

aws_s3 = boto3.client('s3')
BUCKET = BUCKET_NAME


def upload_to_s3(filename):
    try:
        aws_s3.upload_file(Filename='report.csv',
                           Bucket=BUCKET,
                           Key=filename)
        # aws_s3.Bucket(BUCKET).upload_file('/tmp/file.xlsx', 'file.xlsx')
        url = S3_URL + filename
        return url
    except Exception as e:
        print(f"exception due to: {e}")
        return None
