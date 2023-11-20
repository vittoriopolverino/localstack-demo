####################################################
#  archive file
####################################################
data "archive_file" "dockerhub_to_s3_archive_file" {
  type        = "zip"
  source_dir  = "${path.cwd}/"
  output_path = "${path.cwd}/dist/dockerhub_to_s3.zip"

  excludes = [
    ".localstack",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "infra",
    "scripts",
    "src/s3_to_dynamodb",
    "tests",
    ".git",
    ".gitignore",
    ".pre-commit-config.yaml",
    "poetry.lock",
    "pyproject.toml",
    "README.md",
    ".idea",
    ".vscode"
  ]
}

data "archive_file" "s3_to_dynamodb_archive_file" {
  type        = "zip"
  source_dir  = "${path.cwd}/"
  output_path = "${path.cwd}/dist/s3_to_dynamodb.zip"

  excludes = [
    ".localstack",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "infra",
    "scripts",
    "src/dockerhub_to_s3",
    "tests",
    ".git",
    ".gitignore",
    ".pre-commit-config.yaml",
    "poetry.lock",
    "pyproject.toml",
    "README.md",
    ".idea",
    ".vscode"
  ]
}


####################################################
#  policy document
####################################################
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "dockerhub_to_s3_lambda_policy_document" {
  statement {
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.dockerhub_bucket.arn,
      "${aws_s3_bucket.dockerhub_bucket.arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "s3_to_dynamodb_lambda_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*",
      "dynamodb:*"
    ]
    resources = [
      aws_s3_bucket.dockerhub_bucket.arn,
      "${aws_s3_bucket.dockerhub_bucket.arn}/*",
      aws_dynamodb_table.dockerhub_dynamodb_table.arn
    ]
  }
}
