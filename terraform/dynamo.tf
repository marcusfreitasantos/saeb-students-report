resource "aws_dynamodb_table" "saeb_questions_dev" {
  name         = "saeb_questions_dev"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  server_side_encryption {
    enabled = true
  }

  tags = {
    Environment = "dev"
    Project     = "saeb-students-report"
  }
}

resource "aws_dynamodb_table" "saeb_interventions_dev" {
  name         = "saeb_interventions_dev"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "id"
  range_key = "category"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  attribute {
    name = "descriptor"
    type = "S"
  }

  global_secondary_index {
    name            = "GetByCategoryAndDescriptor"
    hash_key        = "category"
    range_key       = "descriptor"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  server_side_encryption {
    enabled = true
  }

  tags = {
    Environment = "dev"
    Project     = "saeb-students-report"
  }
}