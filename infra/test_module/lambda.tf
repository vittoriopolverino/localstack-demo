####################################################
#  function
####################################################
resource "aws_lambda_function" "lambda_function" {
  filename         = data.archive_file.lambda_function_archive_file.output_path
  function_name    = "test-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "src.handler.handler"
  source_code_hash = data.archive_file.lambda_function_archive_file.output_base64sha256
  runtime          = "python3.10"
  memory_size      = 512
  timeout          = 30 # seconds

  layers = []

  environment {
    variables = {
      SQS_QUEUE_URL = aws_sqs_queue.queue.id
    }
  }
}


####################################################
#  event source mapping
####################################################
resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = aws_sqs_queue.queue.arn
  function_name    = aws_lambda_function.lambda_function.arn
  batch_size       = 1
}