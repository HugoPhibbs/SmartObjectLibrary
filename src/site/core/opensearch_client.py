import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch, AWSV4SignerAuth, RequestsHttpConnection, TransportError
import boto3

load_dotenv()

# Script to load the OpenSearch client
__all__ = ["get_client"]


def get_aws_creds(use_default, region):
    if use_default:
        session = boto3.Session(region_name=region)
        print("Using default AWS credentials from environment or IAM role.")
    else:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )

    creds = session.get_credentials().get_frozen_credentials()

    try:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"Auth succeeded: Using AWS Identity: {identity['Arn']}")
    except Exception as e:
        raise EnvironmentError(f"Auth failed: Failed to get AWS identity: {e}")

    return creds


def get_client(stage=None, auth_type=None):
    if stage is None:
        stage = os.getenv("OPENSEARCH_STAGE", "dev")

    if stage == "dev":
        host = os.getenv("OPENSEARCH_HOST", "http://localhost")
        port = os.getenv("OPENSEARCH_PORT", 9200)

        auth = ("admin", os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))
        verify_certs = False
        use_ssl = False
    elif stage == "prod":
        host = os.getenv("OPENSEARCH_HOST_PROD", "not-found")
        port = os.getenv("OPENSEARCH_PORT_PROD", 443)

        region = os.getenv("AWS_REGION", "not-found")

        if auth_type is None:
            auth_type = os.getenv("OPENSEARCH_AUTH_TYPE", "env-vars")

        print(f"Using auth_type: {auth_type}")

        creds = get_aws_creds(use_default=(auth_type == "lambda-role"), region=region)

        auth = AWSV4SignerAuth(creds, region, "es")
        verify_certs = True
        use_ssl = True
    else:
        raise ValueError(f"Unknown OPENSEARCH_STAGE: {stage}")

    print(f"Connecting to OpenSearch at {host}:{port}..., stage={stage}")

    client = OpenSearch(
        [{'host': host, 'port': int(port)}],
        http_auth=auth,
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        connection_class=RequestsHttpConnection,
        ssl_show_warn=False,
        ssl_assert_hostname=False
    )

    try:
        resp = client.transport.perform_request("GET", "/")
        print(f"OS / => {resp}")
    except TransportError as te:
        print(
            f"Error Connecting to OS: TransportError status={getattr(te, 'status_code', None)} body={getattr(te, 'error', None)}")
        raise te

    return client
