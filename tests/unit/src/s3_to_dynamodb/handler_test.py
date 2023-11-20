import datetime

import pytest

from src.s3_to_dynamodb.handler import get_bucket_name, get_latest_objects_by_year_month_from_list


@pytest.mark.parametrize(
    'event, expected',
    [
        (
            {
                'Records': [
                    {'s3': {'bucket': {'name': 'dockerhub'}, 'object': {'key': 'raw/year=2023/month=10/day=30/2023_10_30_154316.json'}}}
                ]
            },
            'dockerhub',
        ),
        (
            {
                'Records': [
                    {'s3': {'bucket': {'name': 'test_bucket'}, 'object': {'key': 'raw/year=1900/month=10/day=30/1900_10_30_154316.json'}}}
                ]
            },
            'test_bucket',
        ),
    ],
)
def test_get_bucket_name(event, expected):
    bucket_name = get_bucket_name(event=event)
    assert isinstance(bucket_name, str)
    assert bucket_name == expected


@pytest.mark.parametrize(
    'objects, expected',
    [
        (  # test 1
            [  # objects
                {'Key': 'raw/year=2023/month=09/day=14/2023_09_14_180000.json'},
                {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_193000.json'},
                {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_200000.json'},
                {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_210000.json'},
            ],
            {  # expected
                '2023-09': {
                    'object': {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_210000.json'},
                    'timestamp': datetime.datetime(2023, 9, 15, 21, 0),
                }
            },
        ),
        (  # test 2
            [  # objects
                {'Key': 'raw/year=2023/month=09/day=14/2023_09_14_180000.json'},
                {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_200000.json'},
                {'Key': 'raw/year=2023/month=10/day=01/2023_10_01_210000.json'},
                {'Key': 'raw/year=2023/month=10/day=31/2023_10_31_010000.json'},
            ],
            {  # expected
                '2023-09': {
                    'object': {'Key': 'raw/year=2023/month=09/day=15/2023_09_15_200000.json'},
                    'timestamp': datetime.datetime(2023, 9, 15, 20, 0),
                },
                '2023-10': {
                    'object': {'Key': 'raw/year=2023/month=10/day=31/2023_10_31_010000.json'},
                    'timestamp': datetime.datetime(2023, 10, 31, 1, 0),
                },
            },
        ),
    ],
)
def test_get_latest_objects_by_year_month_from_list(objects, expected):
    result = get_latest_objects_by_year_month_from_list(objects=objects)
    assert isinstance(result, dict)
    assert result == expected
