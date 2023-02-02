import boto3
import loguru

from botocore.exceptions import ClientError

logger = loguru.logger


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


def get_client():

    session = boto3.Session(profile_name="foul-play")
    ec2client = session.client("ec2")

    return ec2client


def get_resource():

    session = boto3.Session(profile_name="foul-play")
    ec2resource = session.resource("ec2")

    return ec2resource


def list_instances_by_tag_value(client, tagkey, tagvalue):
    try:
        response = client.describe_instances(
            Filters=[{"Name": "tag:" + tagkey, "Values": [tagvalue]}]
        )
        instancelist = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instancelist.append(instance["InstanceId"])
        return instancelist
    except Exception as e:
        logger.exception(f"Something went wrong {e}")


def handler(event):
    logger.info("Application started")

    client = get_client()

    resource = get_resource()

    list_instances = list_instances_by_tag_value(client, event["TagKey"], event["TagValue"])

    if event["action"] == "stop":
        power_off(resource, list_instances)

    if event["action"] == "start":
        power_on(resource, list_instances)

    logger.info("Application finished")


if __name__ == "__main__":
    handler({"action": "start", "TagKey": "Role", "TagValue": "slave"})
