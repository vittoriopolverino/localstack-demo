####################################################
#  role
####################################################
resource "aws_iam_role" "dockerhub_to_s3_role" {
  name               = "dockerhub-to-s3-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role" "s3_to_dynamodb_role" {
  name               = "s3-to-dynamodb-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

####################################################
#  policy
####################################################
resource "aws_iam_policy" "dockerhub_to_s3_lambda_policy" {
  name   = "dockerhub-to-s3-lambda-policy"
  policy = data.aws_iam_policy_document.dockerhub_to_s3_lambda_policy_document.json
}

resource "aws_iam_policy" "s3_to_dynamodb_lambda_policy" {
  name   = "s3-to-dynamodb-lambda-policy"
  policy = data.aws_iam_policy_document.s3_to_dynamodb_lambda_policy_document.json
}


####################################################
#  policy attachment
####################################################
resource "aws_iam_role_policy_attachment" "dockerhub_to_s3_role_policy_attachment" {
  role       = aws_iam_role.dockerhub_to_s3_role.name
  policy_arn = aws_iam_policy.dockerhub_to_s3_lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "s3_to_dynamodb_role_policy_attachment" {
  role       = aws_iam_role.s3_to_dynamodb_role.name
  policy_arn = aws_iam_policy.s3_to_dynamodb_lambda_policy.arn
}
