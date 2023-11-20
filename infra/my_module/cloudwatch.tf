####################################################
#  event rule
####################################################
resource "aws_cloudwatch_event_rule" "dockerhub_to_s3_event_rule" {
  name                = "dockerhub-to-s3-event-rule"
  description         = "trigger lambda function every 1 minute"
  schedule_expression = "rate(5 minutes)"
}


####################################################
#  event target
####################################################
resource "aws_cloudwatch_event_target" "dockerhub_to_s3_event_target" {
  rule      = aws_cloudwatch_event_rule.dockerhub_to_s3_event_rule.name
  arn       = aws_lambda_function.dockerhub_to_s3_function.arn
  target_id = "LambdaFunctionTargetId"
}
