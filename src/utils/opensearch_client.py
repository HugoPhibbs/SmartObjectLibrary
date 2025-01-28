import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()

HOST = "http://localhost"
PORT = 9200

auth = ("admin", os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))

client = OpenSearch(
    f"{HOST}:{PORT}",
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    ssl_assert_hostname=False
)



