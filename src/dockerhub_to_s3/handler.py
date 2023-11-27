from src.dockerhub_to_s3.pipeline import Pipeline


def handler(event, context):
    pipeline = Pipeline()
    pipeline.execute(event=event, context=context)
