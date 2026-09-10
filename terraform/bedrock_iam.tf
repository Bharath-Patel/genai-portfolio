resource "aws_iam_user" "bedrock_portfolio_user" {
  name = "bedrock_portfolio_user"
}

resource "aws_iam_policy" "bedrock_invoke_only" {
  name = "bedrock_invoke_only"
  description = "Least-privilege policy: only allows invoking Bedrock models, nothing else"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_policy" {
  user = aws_iam_user.bedrock_portfolio_user.name
  policy_arn = aws_iam_policy.bedrock_invoke_only.arn
}

