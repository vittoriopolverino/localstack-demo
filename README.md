```
docker-compose up
```

```
http://localhost:4566/health
```

```
docker-ps
```

```
docker exec -it id_container bin/sh
```

```
awslocal s3api list-buckets
```

```
aws s3api list-buckets --query "Buckets[].Name" --endpoint-url=http://localhost:4566
```

```
poetry run localstack --profile=dev start -d
```

```
poetry run tflocal -chdir='infra' init
```

```
poetry run tflocal -chdir='infra' apply --auto-approve
```

```
poetry run awslocal s3api list-buckets
```

```
poetry run awslocal ecr create-repository --repository-name lambda-container-image
```