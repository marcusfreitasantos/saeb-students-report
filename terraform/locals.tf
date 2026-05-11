locals {
  common_tags = {
    Project     = "saeb-students-report"
    Environment = "dev"
    ManagedBy   = "terraform"
    Owner       = "Marcus Freitas"
  }
  
  lambda_build_path = {
    manage_report_questions = "../src/functions/manage_report_questions/.aws-sam/build/ManageReportQuestionsFunction/lambda.zip"
  }

}