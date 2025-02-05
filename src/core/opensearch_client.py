import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()

HOST = os.getenv("OPENSEARCH_HOST")
PORT = os.getenv("OPENSEARCH_PORT")

auth = ("admin", os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))

client = OpenSearch(
    f"{HOST}:{PORT}",
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    ssl_assert_hostname=False
)



