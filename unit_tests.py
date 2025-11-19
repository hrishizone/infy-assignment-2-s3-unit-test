from moto import mock_aws
import boto3
import logging
from s3_ops import Storage_Operations 

logging.basicConfig(filename="logs.log",level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


@mock_aws
def test_add_s3_objects():
    s3 = boto3.client('s3', region_name='ap-south-1')
    bucket_name = 'test-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'}
    )
    logger.info('S3 Bucket Created')
    storage = Storage_Operations(bucket_name)
    storage.add_s3_objects()
    logger.info('Objects added into S3 Bucket')

    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    totalObj = 0
    for page in page_iterator:
        totalObj += page.get('KeyCount', 0)

    logger.info(f'{totalObj} Objects added into S3 Bucket')
    assert totalObj == 1500

@mock_aws
def test_fetch_s3_objects_by_metadata():
    s3 = boto3.client('s3', region_name='ap-south-1')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})

    s3.put_object(Bucket=bucket_name, Key='1.txt', Body='file 1', Metadata={'type': 'report', 'batch': 'batch-1'})
    s3.put_object(Bucket=bucket_name, Key='2.txt', Body='file 2', Metadata={'type': 'report', 'batch': 'batch-2'})
    s3.put_object(Bucket=bucket_name, Key='3.txt', Body='file 3', Metadata={'type': 'log', 'batch': 'batch-1'})

    storage = Storage_Operations(bucket_name)
    result = storage.fetch_s3_objects_by_metadata({'batch': 'batch-1'})

    logger.info(f'Matched Results:{result}')
    assert '1.txt' in result
    assert '2.txt' not in result
    assert '3.txt' in result


@mock_aws
def test_fetch_s3_objects_by_tag():
    s3 = boto3.client('s3', region_name='ap-south-1')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})

    s3.put_object(Bucket=bucket_name, Key='1.txt', Body='File 1', Tagging='Type=Report&Batch=batch-1')
    s3.put_object(Bucket=bucket_name, Key='2.txt', Body='File 2', Tagging='Type=Report&Batch=batch-2')
    s3.put_object(Bucket=bucket_name, Key='3.txt', Body='File 3', Tagging='Type=Log&Batch=batch-1')

    storage = Storage_Operations(bucket_name)
    result = storage.fetch_s3_objects_by_tag({'Batch': 'batch-1'})

    logger.info(f'Matched Results: {result}')
    assert '1.txt' in result
    assert '2.txt' not in result
    assert '3.txt' in result


@mock_aws
def test_delete_s3_objects_by_metadata():
    s3 = boto3.client('s3', region_name='ap-south-1'); 
    bucket_name='test-bucket'
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})

    s3.put_object(Bucket=bucket_name, Key='1.txt', Body='file1', Metadata={'batch': 'batch-1'})
    s3.put_object(Bucket=bucket_name, Key='2.txt', Body='file2', Metadata={'batch': 'batch-1'})
    s3.put_object(Bucket=bucket_name, Key='3.txt', Body='file3', Metadata={'batch': 'batch-2'})

    storage = Storage_Operations(bucket_name)
    result = storage.delete_s3_objects_by_metadata({'batch': 'batch-1'})

    logger.info(f"Deleted: {result['Deleted']}")
    assert result['Deleted'] == 2 



@mock_aws
def test_delete_s3_objects_by_tags():
    s3 = boto3.client('s3', region_name='ap-south-1'); 
    bucket_name='test-bucket'
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})

    s3.put_object(Bucket=bucket_name, Key='1.txt', Body='File 1', Tagging='Type=Report&Batch=batch-1')
    s3.put_object(Bucket=bucket_name, Key='2.txt', Body='File 2', Tagging='Type=Report&Batch=batch-2')
    s3.put_object(Bucket=bucket_name, Key='3.txt', Body='File 3', Tagging='Type=Log&Batch=batch-1')

    storage = Storage_Operations(bucket_name)
    result = storage.delete_s3_objects_by_tags({'Batch': 'batch-1'})

    logger.info(f"Deleted: {result['Deleted']}")
    assert result['Deleted'] == 2


if __name__ == "__main__":
    test_delete_s3_objects_by_metadata()