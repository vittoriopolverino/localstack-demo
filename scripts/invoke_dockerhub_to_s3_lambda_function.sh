#!/usr/bin/env bash

run() {
  poetry run awslocal lambda invoke --function-name dockerhub-to-s3 --payload '{}' --output json src/dockerhub_to_s3/result.json --region us-east-1
}

run

$SHELL
