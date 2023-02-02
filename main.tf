module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  
  function_name = "instance-switcher-func"
  description   = "The lambda function to start the Sync EC2 Instance"
  handler       = "lambda.handler"
  runtime       = "python3.8"

  timeout       = "10"
    publish = true
  create_package         = false
  local_existing_package = "lambda_package/instance-switcher-func.zip"

  attach_policies    = true
    create_role        = true
    number_of_policies = 1
    policies           = [module.iam_policy.policy_name_with_arn["ec2-instance-switcher-policy"]]

  allowed_triggers = {
    Eventbridge_On_Slave = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge_on.eventbridge_rule_arns["instance-slave-switcher-on"]
    }
    Eventbridge_Off_Slave = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge_on.eventbridge_rule_arns["instance-slave-switcher-off"]
    }
    Eventbridge_On_Master = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge_on.eventbridge_rule_arns["instance-master-switcher-on"]
    }
    Eventbridge_Off_Master = {
      principal  = "events.amazonaws.com"
      source_arn = module.eventbridge_on.eventbridge_rule_arns["instance-master-switcher-off"]
    }
  }
}

module "eventbridge_on" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false
  create_role = true
  role_name = "instance-switcher-on"

  rules = {
    "instance-slave-switcher-on" = {
      description         = "Trigger for a Lambda"
      schedule_expression = "cron(0 12 * * ? *)"
    },
    "instance-slave-switcher-off" = {
      description         = "Trigger for a Lambda"
      schedule_expression = "cron(0 21 * * ? *)"
    },
    "instance-master-switcher-on" = {
      description         = "Trigger for a Lambda"
      schedule_expression = "cron(0 12 * * ? *)"
    },
    "instance-master-switcher-off" = {
      description         = "Trigger for a Lambda"
      schedule_expression = "cron(0 21 * * ? *)"
    }
  }

  targets = {
    "instance-slave-switcher-on" = [
      {
        name  = "instance-slave-switcher-on"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({"action": "start", "TagKey": "Role", "TagValue": "slave"})
      }
    ]
    "instance-slave-switcher-off" = [
      {
        name  = "instance-slave-switcher-off"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({"action": "stop", "TagKey": "Role", "TagValue": "slave"})
      }
    ]
    "instance-master-switcher-on" = [
      {
        name  = "instance-master-switcher-on"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({"action": "start", "TagKey": "Role", "TagValue": "master"})
      }
    ]
    "instance-master-switcher-off" = [
      {
        name  = "instance-master-switcher-off"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({"action": "stop", "TagKey": "Role", "TagValue": "master"})
      }
    ]
  }
}

module "iam_policy" {
    source  = "git@github.com:ei-roslyakov/terraform-modules.git//aws_iam_policy"

    policies = {
    "ec2-instance-switcher-policy" = {
      name        = "ec2-instance-switcher-policy"
      policy_path = "./policies/instance-switcher.json"
      description = "Allow turt ON EC2 Instance"
    }
  }
}