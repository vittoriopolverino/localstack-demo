####################################################
#  bucket
####################################################
resource "aws_s3_bucket" "dockerhub_bucket" {
  bucket = "dockerhub"
}


####################################################
#  bucket notification
####################################################
resource "aws_s3_bucket_notification" "dockerhub_bucket_notification" {
  bucket = aws_s3_bucket.dockerhub_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_to_dynamodb_function.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_prefix       = "raw/"
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.s3_to_dynamodb_lambda_permission]
}


####################################################
#  lifecycle configuration
####################################################
resource "aws_s3_bucket_lifecycle_configuration" "dockerhub_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.dockerhub_bucket.id

  rule {
    id     = "cleanup-old-files"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    expiration {
      days = 365
    }
  }
}
