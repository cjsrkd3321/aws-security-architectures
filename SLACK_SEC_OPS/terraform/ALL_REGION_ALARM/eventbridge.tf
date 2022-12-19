# apne2
resource "aws_cloudwatch_event_rule" "apne2" {
  for_each = var.patterns

  provider      = aws.apne2
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_apne2" {
  for_each = aws_cloudwatch_event_rule.apne2

  provider = aws.apne2
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# apne1
resource "aws_cloudwatch_event_rule" "apne1" {
  for_each = var.patterns

  provider      = aws.apne1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_apne1" {
  for_each = aws_cloudwatch_event_rule.apne1

  provider = aws.apne1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# apne3
resource "aws_cloudwatch_event_rule" "apne3" {
  for_each = var.patterns

  provider      = aws.apne3
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_apne3" {
  for_each = aws_cloudwatch_event_rule.apne3

  provider = aws.apne3
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# aps1
resource "aws_cloudwatch_event_rule" "aps1" {
  for_each = var.patterns

  provider      = aws.aps1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_aps1" {
  for_each = aws_cloudwatch_event_rule.aps1

  provider = aws.aps1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# apse1
resource "aws_cloudwatch_event_rule" "apse1" {
  for_each = var.patterns

  provider      = aws.apse1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_apse1" {
  for_each = aws_cloudwatch_event_rule.apse1

  provider = aws.apse1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# apse2
resource "aws_cloudwatch_event_rule" "apse2" {
  for_each = var.patterns

  provider      = aws.apse2
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_apse2" {
  for_each = aws_cloudwatch_event_rule.apse2

  provider = aws.apse2
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# cac1
resource "aws_cloudwatch_event_rule" "cac1" {
  for_each = var.patterns

  provider      = aws.cac1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_cac1" {
  for_each = aws_cloudwatch_event_rule.cac1

  provider = aws.cac1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# euc1
resource "aws_cloudwatch_event_rule" "euc1" {
  for_each = var.patterns

  provider      = aws.euc1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_euc1" {
  for_each = aws_cloudwatch_event_rule.euc1

  provider = aws.euc1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# eun1
resource "aws_cloudwatch_event_rule" "eun1" {
  for_each = var.patterns

  provider      = aws.eun1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_eun1" {
  for_each = aws_cloudwatch_event_rule.eun1

  provider = aws.eun1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# euw1
resource "aws_cloudwatch_event_rule" "euw1" {
  for_each = var.patterns

  provider      = aws.euw1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_euw1" {
  for_each = aws_cloudwatch_event_rule.euw1

  provider = aws.euw1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# euw2
resource "aws_cloudwatch_event_rule" "euw2" {
  for_each = var.patterns

  provider      = aws.euw2
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_euw2" {
  for_each = aws_cloudwatch_event_rule.euw2

  provider = aws.euw2
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# euw3
resource "aws_cloudwatch_event_rule" "euw3" {
  for_each = var.patterns

  provider      = aws.euw3
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_euw3" {
  for_each = aws_cloudwatch_event_rule.euw3

  provider = aws.euw3
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# sae1
resource "aws_cloudwatch_event_rule" "sae1" {
  for_each = var.patterns

  provider      = aws.sae1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_sae1" {
  for_each = aws_cloudwatch_event_rule.sae1

  provider = aws.sae1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# use1
resource "aws_cloudwatch_event_rule" "use1" {
  for_each = var.patterns

  provider      = aws.use1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_use1" {
  for_each = aws_cloudwatch_event_rule.use1

  provider = aws.use1
  rule     = each.value.name
  arn      = module.lambda_function.lambda_function_arn
}

# use2
resource "aws_cloudwatch_event_rule" "use2" {
  for_each = var.patterns

  provider      = aws.use2
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_use2" {
  for_each = aws_cloudwatch_event_rule.use2

  provider = aws.use2
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# usw1
resource "aws_cloudwatch_event_rule" "usw1" {
  for_each = var.patterns

  provider      = aws.usw1
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_usw1" {
  for_each = aws_cloudwatch_event_rule.usw1

  provider = aws.usw1
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}

# usw2
resource "aws_cloudwatch_event_rule" "usw2" {
  for_each = var.patterns

  provider      = aws.usw2
  name          = each.key
  description   = each.key
  event_pattern = each.value
}

resource "aws_cloudwatch_event_target" "default_usw2" {
  for_each = aws_cloudwatch_event_rule.usw2

  provider = aws.usw2
  rule     = each.value.name
  arn      = local.default_bus_arn
  role_arn = aws_iam_role.event_bus_invoke_remote_event_bus.arn
}