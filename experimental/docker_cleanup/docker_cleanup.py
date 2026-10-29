import sys

import docker
from docker.errors import DockerException

# Connect to the Docker daemon
try:
    client = docker.from_env()
    print("[+] Connected to Docker daemon")
except DockerException as e:
    print(f"[-] Failed to connect to Docker daemon: {e}")
    sys.exit(1)

# Cleanup all containers
try:
    client.containers.prune()
    print("[+] Cleaned up containers")
except DockerException as e:
    print(f"[-] Failed to prune containers: {e}")

# Cleanup all images
try:
    client.images.prune({'dangling': True})
    print("[+] Cleaned up images")
except DockerException as e:
    print(f"[-] Failed to prune images: {e}")
else:
    print("[+] Finished Docker cleanup")
