import os
import datetime

import json
import boto3

from urllib.parse import unquote

DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', None)

s3 = boto3.client('s3', endpoint_url=os.environ.get('S3_ENDPOINT_URL', None))
dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ.get('DYNAMODB_ENDPOINT_URL', None))


def get_bucket_name(event: dict) -> str:
    records = event.get('Records', [])
    bucket_name = records[0]['s3']['bucket']['name']
    return bucket_name


def get_object_key(event: dict) -> str:
    records = event.get('Records', [])
    object_key = records[0]['s3']['object']['key']
    # Decode the S3 key to obtain the original form
    # Example: 'raw/year%3D2023/month%3D11/day%3D16/2023_11_16_095024.json' becomes 'raw/year=2023/month=11/day=16/2023_11_16_095024.json'
    decoded_object_key = unquote(object_key)
    return decoded_object_key


def get_latest_objects_by_year_month_from_list(objects: list[dict]) -> dict:
    """
    Retrieve the latest objects for each year/month from a list of objects

    Parameters:
    - objects (list[dict]): A list of dictionaries containing object information

    Returns:
    - dict: A dictionary containing the latest objects, for each year/month.
    """
    latest_files_by_year_month: dict = {}
    for obj in objects:
        object_key = obj['Key']

        # Extract year and month from the file name
        # i.e. '2023_10_30_153000.json' -> 2023_10
        year, month = object_key.split('/')[4].split('.')[0].split('_')[0:2]

        # Extract the timestamp from the file name
        obj_timestamp_str = object_key.split('/')[4].split('.')[0]

        # Convert the timestamp string to a datetime object
        obj_timestamp = datetime.datetime.strptime(obj_timestamp_str, '%Y_%m_%d_%H%M%S')

        # Create the dictionary key
        year_month_key = f'{year}-{month}'

        # Check if this file is more recent than the one already recorded for the same year and month
        if year_month_key not in latest_files_by_year_month or obj_timestamp > latest_files_by_year_month[year_month_key]['timestamp']:
            # If it is more recent, update the latest_files_by_year_month dictionary with the new file information
            latest_files_by_year_month[year_month_key] = {'object': obj, 'timestamp': obj_timestamp}
    return latest_files_by_year_month


def get_latest_objects_by_year_month_from_bucket(bucket_name: str, prefix: str) -> dict:
    """
    Retrieve the latest objects from an S3 bucket with the specified prefix.

    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - prefix (str): The prefix to filter objects in the bucket.

    Returns:
    - dict: A dictionary containing the latest objects, grouped by year-month.
    """
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    objects = response.get('Contents', [])
    latest_files_by_year_month = get_latest_objects_by_year_month_from_list(objects=objects)
    return latest_files_by_year_month


def create_aggregated_metrics_by_year_month(data: dict, bucket_name: str) -> dict:
    """
    Create aggregated metrics for each year and month from the input dataset.

    Parameters:
    - data (dict): Dictionary containing the latest files grouped by year and month.
    - bucket_name (str): The name of the S3 bucket.

    Returns:
    - dict: Aggregated metrics for each year and month.
    """
    aggregated_metrics_by_year_month: dict = {}
    for key, obj_info in data.items():
        # print(f"year-month: {key}, Latest File: {obj_info['object']['Key']}")
        object_key = obj_info['object']['Key']
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        file_content_json = json.loads(file_content)
        star_count = file_content_json.get('star_count', None)
        pull_count = file_content_json.get('pull_count', None)
        if key not in aggregated_metrics_by_year_month:
            aggregated_metrics_by_year_month[key] = []
        aggregated_metrics_by_year_month[key].append({'star_count': star_count, 'pull_count': pull_count})

    return aggregated_metrics_by_year_month


def handler(event, context):
    try:
        print(event)

        # extract bucket and object from the s3 event notification
        bucket_name = get_bucket_name(event=event)
        object_key = get_object_key(event=event)

        # Retrieve the content of the S3 file
        file_content = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content_json = json.loads(file_content['Body'].read().decode('utf-8'))

        # Extract values from the file_content_json dictionary
        user = file_content_json.get('user', 'n/a')
        name = file_content_json.get('name', 'n/a')
        namespace = file_content_json.get('namespace', 'n/a')
        star_count = file_content_json.get('star_count', None)
        pull_count = file_content_json.get('pull_count', None)
        last_updated = file_content_json.get('last_updated', None)

        # Calculate the TTL (Time to Live) epoch timestamp for DynamoDB item
        # This sets the expiration time for the item to 60 days from the current UTC time
        ttl_epoch = int((datetime.datetime.utcnow() + datetime.timedelta(days=60)).timestamp())

        # Retrieve the latest file for each year and month from the 'raw' prefix in the specified S3 bucket
        latest_file_by_year_month = get_latest_objects_by_year_month_from_bucket(bucket_name=bucket_name, prefix='raw')

        # Create aggregated metrics
        aggregated_metrics_by_year_month = create_aggregated_metrics_by_year_month(data=latest_file_by_year_month, bucket_name=bucket_name)

        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

        # PK: partition key including user, name, and namespace
        partition_key = f'#user#{user}#name#{name}#namespace#{namespace}'

        # SK: sort key including the timestamp from the last_updated key
        sort_key = f'#timestamp#{last_updated}'

        table.put_item(
            Item={
                'PK': partition_key,
                'SK': sort_key,
                'star_count': star_count,
                'pull_count': pull_count,
                'last_updated': last_updated,
                'aggregated_metrics_by_year_month': aggregated_metrics_by_year_month,
                'TTL': ttl_epoch,
            }
        )

        is_latest_version = True
        response = table.get_item(Key={'PK': partition_key, 'SK': '#latest_version'}, ProjectionExpression='last_updated')

        if 'Item' in response:
            existing_last_updated = response['Item'].get('last_updated', None)
            if existing_last_updated and last_updated < existing_last_updated:
                is_latest_version = False

        if is_latest_version:
            table.put_item(Item={'PK': partition_key, 'SK': '#latest_version', 'last_updated': last_updated, 'TTL': ttl_epoch})

        return {'statusCode': 200, 'body': json.dumps({'message': 'S3 to DynamoDB - Request processed successfully'})}
    except Exception as exception:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'{type(exception)} - {str(exception)}', 'error': 'Internal Server Error'}),
        }
