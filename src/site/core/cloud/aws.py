import os

import boto3


def get_aws_session(use_default, region="ap-southeast-2"):
    if use_default:
        session = boto3.Session(region_name=region)
        print("Using default AWS credentials from environment or IAM role.")
    else:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )

    try:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"Auth succeeded: Using AWS Identity: {identity['Arn']}")
    except Exception as e:
        raise EnvironmentError(f"Auth failed: Failed to get AWS identity: {e}")

    return session


def get_session_creds(session):
    return session.get_credentials().get_frozen_credentials()


def get_s3_client():
    session = get_aws_session(use_default=True)
    return session.client('s3')