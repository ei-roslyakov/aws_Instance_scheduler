# AWS Instance scheduler

This project is created to power ON and power OFF AWS EC2 instances by cron using AWS Lambda and AWS EventBridge.

# Prerequisites

* Terraform >= 0.13.1
* Configured AWS profile with correct access(IAM,S3,Lambda,EventBridge)
* Make

To filter which instance should be triggered, AWS lambda uses a tag, you can change it in Terraform code EventBridge module (TagKey\TagValue).
As well you can define the action which AWS Lambda should perform (start\stop)

```hcl
targets = {
    "instance-slave-switcher-on" = [
      {
        name  = "instance-slave-switcher-on"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({"action": "start", "Tags": {"Role": "master", "Name": "fpla-jmeter-master-ec2"})
      }
    ]
  }
```

# Deployment
* To build the Lambda package, run the command.
```
make build 
```
* To deploy the Terraform code, you have to modify the provider.tf and backend.tf files. Please put the correct value for the profile, region, bucket name, etc. After this you will be able to run command to deploy the infrastructure.
```
terraform init
terraform apply
```

$ To use locally

```
python3 ./lambda.py --tags Role=master Name=fpla-jmeter-master-ec2 --profile foul-play
```


