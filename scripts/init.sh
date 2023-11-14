#!/usr/bin/env bash

start_localstack() {
  poetry run localstack --profile=dev start -d
}


terraform_init() {
  poetry run tflocal -chdir='infra' init
  poetry run tflocal -chdir='infra' fmt
  poetry run tflocal -chdir='infra' apply --auto-approve
}

invoke_lambda_function() {
  poetry run awslocal lambda invoke --function-name test-function --payload '{}' --output json src/result.json
}

init() {
  start_localstack
  terraform_init
  invoke_lambda_function
}

init

$SHELL
