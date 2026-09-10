resource "aws_iam_access_key" "bedrock_user_key" {
  user = aws_iam_user.bedrock_portfolio_user.name
}

output "access_key_id" {
  value = aws_iam_access_key.bedrock_user_key.id
}

output "secret_access_key" {
  value = aws_iam_access_key.bedrock_user_key.secret
  sensitive = true
}