
# 📜 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Architecture](#architecture)
  - [1. Cloud Watch](#1_cloud_watch)
  - [2. Lambda Function](#2_lambda_function)
  - [3. S3](#3_s3)
    - [3.1 Partitioning](#3_1_partitioning)
    - [3.2 Lifecycle Rule](#3_2_lifecycle_rule)
  - [4. S3 Event Notifications](#4_s3_event_notifications)
  - [5. Lambda Function](#5_lambda_function)
  - [6. DynamoDB](#6_dynamodb)
    - [6.1 Single Table Design](#6_1_single_table_design)
    - [6.2 Aggregations](#6_2_aggregations)
    - [6.3 Marker Item](#6_3_marker_item)
    - [6.4 Time to Live](#6_4_ttl)
  - [7. Improvements](#7_improvements)
- [Test](#test)
- [Built Using](#built_using)
- [Authors](#authors)

<br />

# 🤓 About <a name = "about"></a>
The project relies exclusively on open-source services feature available in the LocalStack Community Edition. 

Given that Amazon Elastic Container Registry (ECR) and Lambda Layers are exclusively accessible with the Pro version,, 
I opted for simplicity and ease of use. Consequently, a decision was made to design a solution that steers clear of using external libraries  facilitating a smoother deployment process for the Lambda Function.
<br />

<br />

# 🏁 Getting Started <a name = "getting_started"></a>
Before you begin with the project, make sure you have Poetry installed on your machine. 
If not, you can install it by following the instructions on the [official Poetry installation page](https://python-poetry.org/docs/#installation).

<br />

To install the project dependencies, execute the following command:
```bash
source scripts/poetry_init.sh 
```
Once the script completes, you'll be ready to start working on your Python project with all dependencies in place.

<br />

To run LocalStack and set up the infrastructure that supports the application, run the following command:
```bash
source scripts/localstack_init.sh 
```
The script execution will take care of the following operations:
- Start LocalStack.
- Provision the infrastructure using Terraform.
- Upload data to S3.
- Trigger the Lambda function to extract data from the Docker endpoint.
- Show the stored data in the DynamoDB table.

<br />

<br />


# 🏦 Architecture <a name = "architecture"></a>
![architecture.png](imgs%2Farchitecture.png)

## 1. CloudWatch Event <a name = "1_cloud_watch"></a>
A CloudWatch event rule has been configured to invoke the **"dockerhub-to-s3"** Lambda function at regular five-minute intervals.

## 2. Lambda Function (dockerhub-to-s3) <a name = "2_lambda_function"></a>
The **'dockerhub-to-s3'** Lambda function triggered by CloudWatch, is responsible for retrieving data from the Docker endpoint and storing it in an S3 bucket. 

The data extracted from Docker includes a JSON attribute, **"last_updated"** which serves as the key for partitioning and organizing the stored data within the S3 bucket.
For example:
- raw/year=YYYY/month=MM/day=DD/YYYY_MM_DD_HHMMSS.json
- raw/year=2023/month=09/day=15/2023_09_15_1505500.json
- raw/year=2023/month=09/day=15/2023_09_15_154316.json
- raw/year=2023/month=09/day=15/2023_09_15_200000.json
- raw/year=2023/month=10/day=30/2023_10_30_154316.json


## 3. S3 <a name = "3_s3"></a>
The decision to store data on S3 is centered around simplifying organizational-level data access. 
Once data is on the data lake, it becomes effortlessly shareable with other services like Redshift, Athena, DynamoDB, and more. 
Leveraging S3 event notifications further enables the creation of event-based workflow.

### 3.1 Partitioning <a name = "3_1_partitioning"></a>
The adoption of a partitioning structure not only significantly enhances data retrieval efficiency through optimized search algorithms but also results in cost reductions for services like Athena. This is achieved by strategically applying query filters, thereby avoiding unnecessary full scans of files stored in the data lake.

### 3.2 Lifecycle Rules <a name = "3_2_lifecycle_rule"></a>
Objects with the "raw/" prefix are deleted after 365 days, a practice enforced through lifecycle rules.
Alternatively, the files could be transitioned to a more cost-effective storage class.

## 4. S3 Event Notifications <a name = "4_s3_event_notifications"></a>
Upon the Lambda function uploading a file to S3, an S3 event notification is triggered. The event notification is specifically configured to invoke the **"s3-to-dynamodb"** Lambda function, establishing an automated workflow in response to file uploads on S3.

## 5. Lambda Function (s3-to-dynamodb) <a name = "5_lambda_function"></a>
The **"s3-to-dynamodb"** Lambda function reads the file that triggered the event and saves its content to DynamoDB. 

Within this Lambda function, aggregations are computed for the star_count and pull_count metrics on a yearly/monthly basis. This process is facilitated by employing a partitioning structure (e.g., year/month/day/*) and adhering to a naming convention for the files (e.g., 'YYYY_MM_DD_HHMMSS.json'). These design choices enable the implementation of various strategies for sorting and retrieving files.

For the sake of simplicity, in this particular scenario, the file name serves as the search criterion. 
For each combination of year/month, only the most recent file is considered when generating the metrics aggregations.

## 6. DynamoDB <a name = "6_dynamodb"></a>

### 6.1 Single Table Design <a name = "6_1_single_table_design"></a>
The DynamoDB table is designed with a single-table approach, exemplified by the following PutItem operation:
```python
table.put_item(Item={
    "PK": partition_key,
    "SK": sort_key,
    "star_count": star_count,
    "pull_count": pull_count,
    "last_updated": last_updated,
    "aggregated_metrics_by_year_month": aggregated_metrics_by_year_month,
    "TTL": ttl_epoch
})
```
<br />

The partition key is structured as:
```python
partition_key = f"#user#{user}#name#{name}#namespace#{namespace}"
partition_key = "#user#localstack#name#localstack#namespace#localstack"
```

<br />

The sort key is structured as:
```python
sort_key = f"#timestamp#{last_updated}"
sort_key = #timestamp#2023-09-15T15:00:00.087021Z

```

This design facilitates straightforward queries on the sort key, 
enabling retrieval of items based on specific timeframes, 
such as year, year/month, or year/month/day down to minutes and seconds, using constructs like "contains" and "beginswith."

<br />

### 6.2 Aggregations <a name = "6_2_aggregations"></a>
Aggregated metrics for each year/month are stored in the **"aggregated_metrics_by_year_month"** attribute.

Here is an example of how aggregated metrics information might be stored in the aggregated_metrics_by_year_month attribute in DynamoDB:
```json
"aggregated_metrics_by_year_month": {
    "M": {
        "2023-10": {
            "L": [
                {
                    "M": {
                        "star_count": {
                            "N": "230"
                        },
                        "pull_count": {
                            "N": "185000000"
                        }
                    }
                }
            ]
        },
        "2023-11": {
            "L": [
                {
                    "M": {
                        "star_count": {
                            "N": "277"
                        },
                        "pull_count": {
                            "N": "188599872"
                        }
                    }
                }
            ]
        },
        "2023-09": {
            "L": [
                {
                    "M": {
                        "star_count": {
                            "N": "201"
                        },
                        "pull_count": {
                            "N": "180000050"
                        }
                    }
                }
            ]
        }
    }
}
```
<br />

### 6.3 Marker Item <a name = "6_3_marker_item"></a>
With every insertion into the DynamoDB table, an item is explicitly designed to keep track of the most recent entry. 
By having this dedicated marker item, queries seeking the most recent data can efficiently identify the relevant entry without the need for extensive scans through historical records. 

The item is structured as follows:
```json
{
    "SK": {
        "S": "#latest_version"
    },
    "last_updated": {
        "S": "2023-11-18T22:01:11.395251Z"
    },
    "PK": {
        "S": "#user#localstack#name#localstack#namespace#localstack"
    },
    "TTL": {
        "N": "1705513319"
    }
}
```
<br />

The partition key is structured as:
```python
partition_key = f"#user#{user}#name#{name}#namespace#{namespace}"
partition_key = "#user#localstack#name#localstack#namespace#localstack"
```

<br />

The sort key is structured as:
```python
sort_key = "#latest_version"
```
<br />

### 6.4 Time to Live <a name = "6_4_ttl"></a>
The item in the DynamoDB table includes a TTL attribute, which stands for Time to Live. 
This attribute is configured to specify the expiration time of the item. 
In this particular case, every time an item is inserted into the table, the TTL is set with a predefined expiration of 60 days.


## 7. Improvements <a name = "7_improvements"></a>

- **Optimize CloudWatch Event Rule Interval:** Explore the optimal time interval for the CloudWatch Event Rule. Invoking the Lambda function every 5 minutes may be excessive and unnecessary
- **Refine Data Partitioning Strategy:** Investigate by considering and anticipating how the data is expected to be used and queried (S3, DynamoDB). Identifying the optimal partition key and strategy can significantly enhance data retrieval efficiency.
- **Improve S3 Event Consumption:** Consider introducing an SNS topic for S3 event notifications rather than directly invoking the Lambda function. This enables the SNS topic to serve multiple subscribers in the future. In conjunction with the SNS topic, integrate an SQS queue before invoking the Lambda function. If needed, the SQS can reduce the number of invocations if events are processed in batches.
- **Refine Lifecycle Rules and TTL:** Appropriately configure lifecycle rules on the S3 bucket and TTL in the DynamoDB table

<br />

# 🐛 Test <a name = "test"></a>
Tests are automatically executed through the pre-commit hook when pushing to the remote branch:
``` yml
  - repo: local
    hooks:
        - id: tests
          name: tests
          entry: poetry run pytest -s
          language: python
          "types": [ python ]
          pass_filenames: false
          stages: [ push ]
```


Alternatively, tests can also be run manually using the command 
```bash
poetry run pytest
```

<br />

# ⛏️ Built Using <a name = "built_using"></a>
- [Python](https://www.python.org/) | Programming language
- [Poetry](https://python-poetry.org/) | Dependency management and packaging
- [Pre-Commit](https://pre-commit.com/) | Pre-commit task automation
- [Bash](https://www.gnu.org/software/bash/) | Scripting
- [AWS](https://aws.amazon.com/) | Cloud Provider
- [LocalSTack](https://www.localstack.cloud/) | Cloud Service Emulator
- [Terraform](https://www.terraform.io/) | IaC

<br />

<br />

# ✏️ Authors <a name = "authors"></a>
Made with ❤️  by Vittorio Polverino

<br />

<br />