####################################################
#  function
####################################################
resource "aws_lambda_function" "dockerhub_to_s3_function" {
  filename         = data.archive_file.dockerhub_to_s3_archive_file.output_path
  function_name    = "dockerhub-to-s3"
  role             = aws_iam_role.dockerhub_to_s3_role.arn
  handler          = "src.dockerhub_to_s3.handler.handler"
  source_code_hash = data.archive_file.dockerhub_to_s3_archive_file.output_base64sha256
  runtime          = "python3.11"
  memory_size      = 1024
  timeout          = 20 # seconds

  environment {
    variables = {
      DOCKER_API_URL  = "https://hub.docker.com/v2/repositories/localstack/localstack/"
      S3_ENDPOINT_URL = "http://s3.localhost.localstack.cloud:4566"
      BUCKET_NAME     = aws_s3_bucket.dockerhub_bucket.id
    }
  }
}

resource "aws_lambda_function" "s3_to_dynamodb_function" {
  filename         = data.archive_file.s3_to_dynamodb_archive_file.output_path
  function_name    = "s3-to-dynamodb"
  role             = aws_iam_role.s3_to_dynamodb_role.arn
  handler          = "src.s3_to_dynamodb.handler.handler"
  source_code_hash = data.archive_file.s3_to_dynamodb_archive_file.output_base64sha256
  runtime          = "python3.11"
  memory_size      = 1024
  timeout          = 20 # seconds

  environment {
    variables = {
      S3_ENDPOINT_URL       = "http://s3.localhost.localstack.cloud:4566"
      DYNAMODB_ENDPOINT_URL = "http://localhost.localstack.cloud:4566"
      DYNAMODB_TABLE_NAME   = "dockerhub_stats"
    }
  }
}


####################################################
#  permission
####################################################
resource "aws_lambda_permission" "dockerhub_to_s3_lambda_permission" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dockerhub_to_s3_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dockerhub_to_s3_event_rule.arn
}

resource "aws_lambda_permission" "s3_to_dynamodb_lambda_permission" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_to_dynamodb_function.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.dockerhub_bucket.arn
}
