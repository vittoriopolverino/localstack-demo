####################################################
#  queue
####################################################
resource "aws_sqs_queue" "queue" {
  name                      = "test-queue"
  delay_seconds             = 0
  max_message_size          = 256000
  message_retention_seconds = 345600  # 4 giorni
}