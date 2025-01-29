import threading
from src.utils.opensearch_start import stop_opensearch, start_opensearch
from src.api.main_api import app


def run_opensearch():
    stop_opensearch()
    start_opensearch()


def run_flask():
    app.run()


if __name__ == "__main__":
    opensearch_thread = threading.Thread(target=run_opensearch)
    opensearch_thread.start()

    run_flask()
