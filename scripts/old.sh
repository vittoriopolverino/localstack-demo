#!/usr/bin/env bash

set_aws_credentials() {
  export AWS_ACCESS_KEY="test"
  export AWS_SECRET_ACCESS_KEY="test"
  export AWS_REGION="eu-central-1"
}

terraform_init() {
  terraform -chdir='infra' init
  terraform -chdir='infra' fmt
  terraform -chdir='infra' plan
  terraform -chdir='infra' apply --auto-approve
}

copy_file_to_s3() {
  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    aws --region eu-central-1 --endpoint-url http://localhost:4566 s3 cp example.txt s3://test-bucket/
}

init() {
  set_aws_credentials
  terraform_init
  copy_file_to_s3
}

init

$SHELL
