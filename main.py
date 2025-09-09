from src.site.api.main_api import app
import src.scripts.objects.upload_from_json as upload_from_json
import argparse

parser = argparse.ArgumentParser(description="Run the object library API server.")

parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=5000)
parser.add_argument("--fill-opensearch", "-fos", action="store_true", help="Fill OpenSearch with initial data")
args = parser.parse_args()

if args.fill_opensearch:
    upload_from_json.main()

if __name__ == "__main__":
    app.run(host=args.host, port=args.port)
