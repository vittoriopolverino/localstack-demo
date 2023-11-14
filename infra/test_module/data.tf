data "aws_iam_policy_document" "lambda_policy_document" {
  statement {
    effect  = "Allow"
    actions = [
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:SendMessage"
    ]
    resources = [
      aws_sqs_queue.queue.arn
    ]
  }
}



####################################################
#  archive file
####################################################
data "archive_file" "lambda_function_archive_file" {
  type        = "zip"
  source_dir  = "${path.cwd}/"
  output_path = "${path.cwd}/dist/test_function.zip"

  excludes = [
    ".localstack",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "infra",
    "scripts",
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