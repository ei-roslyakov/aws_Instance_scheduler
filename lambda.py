import boto3
import argparse
import loguru

from botocore.exceptions import ClientError

logger = loguru.logger


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--profile",
        required=False,
        type=str,
        default=None,
        action="store",
        help="AWS Profile",
    )
    parser.add_argument(
        "--tags", nargs="*", required=False, default=None, action=keyvalue
    )

    return parser.parse_args()


class keyvalue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            key, value = value.split("=")
            getattr(namespace, self.dest)[key] = value


def power_off(client, list_instacnes):

    try:
        for instane in list_instacnes:
            logger.info(f"Instance {instane} is going to shutdown")
            client.instances.filter(InstanceIds=[instane]).stop()
    except ClientError as e:
        logger.exception(f"Client Error: {e}")
    except Exception as e:
        logger.exception(f"Something went wrong {e}")


def power_on(client, list_instacnes):
    try:
        for instane in list_instacnes:
            logger.info(f"Instance {instane} is going to power on")
            client.instances.filter(InstanceIds=[instane]).start()
    except ClientError as e:
        logger.exception(f"Client Error: {e}")
    except Exception as e:
        logger.exception(f"Something went wrong {e}")


def get_client(profile):

    session = boto3.Session(profile_name=profile)
    ec2client = session.client("ec2")

    return ec2client


def get_resource(profile):

    session = boto3.Session(profile_name=profile)
    ec2resource = session.resource("ec2")

    return ec2resource


def list_instances_by_tag_value(client, tags):

    filter = [{"Name": "tag:" + key, "Values": [value]} for key, value in tags.items()]

    try:
        response = client.describe_instances(Filters=filter)
        instancelist = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instancelist.append(instance["InstanceId"])
        return instancelist
    except Exception as e:
        logger.exception(f"Something went wrong {e}")


def handler(event):
    logger.info("Application started")

    args = parse_args()

    tags = args.tags
    if args.tags is None:
        tags = event["Tags"]

    client = get_client(args.profile)

    resource = get_resource(args.profile)

    list_instances = list_instances_by_tag_value(client, tags)

    print(list_instances)

    if event["action"] == "stop":
        power_off(resource, list_instances)

    if event["action"] == "start":
        power_on(resource, list_instances)

    logger.info("Application finished")


if __name__ == "__main__":
    handler(
        {"action": "start", "Tags": {"Role": "master", "Name": "fpla-jmeter-master-ec"}}
    )
