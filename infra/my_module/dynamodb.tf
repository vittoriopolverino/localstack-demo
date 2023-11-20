####################################################
#  table
####################################################
resource "aws_dynamodb_table" "dockerhub_dynamodb_table" {
  name                        = "dockerhub_stats"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = false
  hash_key                    = "PK"
  range_key                   = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  tags = {
    Name = "dynamodb-table-test"
  }
}
