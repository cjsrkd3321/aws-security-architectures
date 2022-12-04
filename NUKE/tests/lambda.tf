# LAMBDAFunctions
resource "aws_lambda_function" "this" {
  function_name    = "nuke-function"
  handler          = "index.test"
  runtime          = "nodejs16.x"
  role             = aws_iam_role.lambda.arn
  filename         = "./resources/nuke_lambda.zip"
  source_code_hash = filebase64sha256("./resources/nuke_lambda.zip")
}