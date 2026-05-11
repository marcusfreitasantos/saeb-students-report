resource "aws_s3_bucket" "bucket-dev" {
  bucket = "saeb-student-report-dev"
  tags = local.common_tags
}