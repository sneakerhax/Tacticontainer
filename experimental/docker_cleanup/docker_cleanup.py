import docker

# Connect to the Docker daemon
client = docker.from_env()

# Cleanup all containers
client.containers.prune()

# Cleanup all images
client.images.prune({'dangling': True})
