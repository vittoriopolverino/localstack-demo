import datetime

import pytest


@pytest.mark.parametrize('date_str, expected', [('date_str_params_1', 'datetime_params_1'), ('date_str_params_2', 'datetime_params_2')])
def test_convert_to_datetime(request, pipeline, date_str, expected):
    date_str = request.getfixturevalue(date_str)
    expected = request.getfixturevalue(expected)
    result = pipeline.convert_to_datetime(date_str=date_str)
    assert isinstance(result, datetime.datetime)
    assert result == expected


@pytest.mark.parametrize('date, expected', [('datetime_params_1', 'object_key_params_1'), ('datetime_params_2', 'object_key_params_2')])
def test_format_object_key(request, pipeline, date, expected):
    date = request.getfixturevalue(date)
    expected = request.getfixturevalue(expected)
    result = pipeline.format_object_key(date=date)
    assert result == expected


@pytest.mark.parametrize('data, object_key', [('data_params_1', 'object_key_params_1'), ('data_params_2', 'object_key_params_2')])
def test_upload_to_s3(request, pipeline, data, object_key):
    data = request.getfixturevalue(data)
    object_key = request.getfixturevalue(object_key)

    pipeline.data = data
    pipeline.object_key = object_key

    result = pipeline.upload_to_s3(data=data, bucket_name=pipeline.bucket_name, object_key=object_key)
    objects = pipeline.s3.list_objects(Bucket=pipeline.bucket_name)['Contents']

    for obj in objects:
        print(f"{obj['Key']=}")

    uploaded_object_keys = [obj['Key'] for obj in objects]

    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    assert object_key in uploaded_object_keys
