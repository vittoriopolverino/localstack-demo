def test_handler(pipeline):
    result = pipeline.execute(event={}, context=None)
    assert result.get('statusCode', None) == 200
