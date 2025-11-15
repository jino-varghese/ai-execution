output "website_url" {
  description = "URL of the static website hosted on S3"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket hosting the frontend"
  value       = aws_s3_bucket.frontend.id
}

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.api.name}/generate-itinerary"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.itinerary_generator.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.itinerary_generator.arn
}

output "region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "deployment_instructions" {
  description = "Next steps after deployment"
  value = <<-EOT

    ================================
    Deployment Successful!
    ================================

    1. Website URL: http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}

    2. API Endpoint: ${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.api.name}/generate-itinerary

    3. Next Steps:
       - Update frontend/js/app.js with the API endpoint URL
       - Re-upload the updated app.js to S3:
         aws s3 cp frontend/js/app.js s3://${aws_s3_bucket.frontend.id}/js/app.js
       - Visit the website URL and test the application

    4. To update Lambda function:
       terraform apply -replace="aws_lambda_function.itinerary_generator"

    5. To destroy all resources:
       terraform destroy

    ================================
  EOT
}
