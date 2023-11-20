#!/usr/bin/env bash

localstack_start() {
  echo "###########################################################"
  echo "Starting LocalStack ..."
  echo "###########################################################"
  poetry run localstack --profile=dev start -d
}

localstack_stop() {
  poetry run localstack stop
}

terraform_init() {
  echo "###########################################################"
  echo "Initializing Terraform ..."
  echo "###########################################################"
  poetry run tflocal -chdir='infra' init
  poetry run tflocal -chdir='infra' fmt
  poetry run tflocal -chdir='infra' apply --auto-approve
}

s3_init() {
  echo "###########################################################"
  echo "Initializing S3 data ..."
  echo "###########################################################"
  for file in src/dockerhub_to_s3/mock/*.json; do
    filename=$(basename -- "$file")
    echo "$filename"
    year=${filename:0:4}
    month=${filename:5:2}
    day=${filename:8:2}
    destination="s3://dockerhub/raw/year=${year}/month=${month}/day=${day}/${filename}"
    poetry run awslocal s3 cp "$file" "$destination" --region us-east-1
    # poetry run awslocal s3 cp src/dockerhub_to_s3/mock/2023_09_14_150000.json s3://dockerhub/raw/year=2023/month=09/day=14/2023_09_14_150000.json --region us-east-1
    sleep 1
  done
  sleep 2
}

dockerhub_to_s3_lambda_function_start() {
  echo "###########################################################"
  echo "Invoking the lambda function 'dockerhub_to_s3' ..."
  echo "###########################################################"
  poetry run awslocal lambda invoke --function-name dockerhub-to-s3 --payload '{}' --output json src/dockerhub_to_s3/result.json --region us-east-1
}

dynamodb_table_scan()  {
  echo "###########################################################"
  echo "Scanning the 'dockerhub_stats' dynamodb table ..."
  echo "###########################################################"
  # poetry run awslocal dynamodb list-tables --region us-east-1
  # poetry run awslocal dynamodb describe-table --table-name dockerhub_stats --region us-east-1
  poetry run awslocal dynamodb scan --table-name dockerhub_stats --region us-east-1
}

get_bucket_objects() {
  poetry run awslocal s3 ls s3://dockerhub/ --recursive
}

init() {
  localstack_start
  terraform_init
  s3_init
  dockerhub_to_s3_lambda_function_start
  dynamodb_table_scan
}

init

$SHELL
