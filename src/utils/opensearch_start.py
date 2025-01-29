import subprocess
import src.utils.upload_beams as upload_beams

COMPOSE_FILE = r"C:\Users\hugop\Documents\Work\SteelProductLibrary\docker-compose.yml"



def start_opensearch():
    subprocess.run(f"docker compose -f {COMPOSE_FILE} up", shell=True)


def stop_opensearch():
    subprocess.run(f"docker compose -f {COMPOSE_FILE} down", shell=True)

if __name__ == "__main__":
    stop_opensearch()
    start_opensearch()

    upload_beams.main()

