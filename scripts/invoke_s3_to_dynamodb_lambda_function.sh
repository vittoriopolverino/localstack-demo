#!/usr/bin/env bash

run() {
  poetry run awslocal lambda invoke --function-name s3-to-dynamodb --cli-binary-format raw-in-base64-out --payload file://src/s3_to_dynamodb/mock/mock_s3_event_notifications.json --output json src/s3_to_dynamodb/result.json --region us-east-1
}

run

$SHELL
