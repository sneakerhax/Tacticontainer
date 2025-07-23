import sys
from pathlib import Path
import docker


def get_docker_client():
    """Return a Docker client connected to the local Docker daemon with error handling."""
    try:
        client = docker.from_env()
        # Test connection
        client.ping()
        return client
    except docker.errors.DockerException as e:
        print(f"[-] Failed to connect to Docker daemon: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error while connecting to Docker: {e}")
        sys.exit(1)


def build_image(docker_client, image, tool_dir):
    """Build a Docker image from the specified tool directory."""
    print(f"[+] Building image {str(image.capitalize())}")
    try:
        if Path.exists(tool_dir):
            docker_client.images.build(path=str(tool_dir), rm=True, tag=image)
        else:
            print("[-] Path to Dockerfile does not exist")
            sys.exit(1)
    except docker.errors.BuildError as e:
        print(f"[-] Failed to build Docker image: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error during build: {e}")
        sys.exit(1)


def run_container(image, docker_client, target, command, volume):
    """Run a Docker container for the specified image and arguments."""
    if volume:
        print(f"[+] Running container {str(image.capitalize())} with target file: {Path(volume[0].split(':')[0]).name}")
    else:
        print(f"[+] Running container {str(image.capitalize())} on target {str(target)}")
    try:
        if image == "nmap":
            if volume:
                if command:
                    container_output = docker_client.containers.run(image, remove=True, command=["-iL", "/targets.txt"] + command, volumes=volume)
                else:
                    container_output = docker_client.containers.run(image, remove=True, command=["-iL", "/targets.txt"], volumes=volume)
            elif command:
                container_output = docker_client.containers.run(image, remove=True, command=command)
            else:
                container_output = docker_client.containers.run(image, remove=True, command=target)
        elif image == "nmap-small":
            if command:
                container_output = docker_client.containers.run(image, remove=True, command=command)
            else:
                container_output = docker_client.containers.run(image, remove=True, command=target)
        elif image == "whatweb":
            container_output = docker_client.containers.run(image, remove=True, command=["--color=never", target])
        elif image == "dirsearch":
            container_output = docker_client.containers.run(image, remove=True, command=["--no-color", "-q", "-u", target])
        elif image == "subfinder":
            container_output = docker_client.containers.run(image, remove=True, command=["-d", target])
        elif image == "naabu":
            if command:
                container_output = docker_client.containers.run(image, remove=True, command=command)
            else:
                container_output = docker_client.containers.run(image, remove=True, command=["-host", target])
        elif image == "httpx":
            if command:
                container_output = docker_client.containers.run(image, remove=True, command=command)
            else:
                container_output = docker_client.containers.run(image, remove=True, command=["-u", target])
        elif image == "nuclei":
            if command:
                container_output = docker_client.containers.run(image, remove=True, command=command)
            else:
                container_output = docker_client.containers.run(image, remove=True, command=["-u", target])
        else:
            raise ValueError(f"Unsupported image: {image}")
        return container_output
    except docker.errors.ContainerError as e:
        print(f"[-] Container error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        sys.exit(1)
