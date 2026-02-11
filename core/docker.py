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


def run_nmap(docker_client, image, target, command, volume):
    if volume:
        volume_command = (command if command else []) + ["-iL", "/targets.txt"]
        return docker_client.containers.run(image, remove=True, command=volume_command, volumes=volume)
    return docker_client.containers.run(image, remove=True, command=(command + [target] if command else target))

def run_nmap_small(docker_client, image, target, command, volume):
    if volume:
        volume_command = (command if command else []) + ["-iL", "/targets.txt"]
        return docker_client.containers.run(image, remove=True, command=volume_command, volumes=volume)
    return docker_client.containers.run(image, remove=True, command=(command + [target] if command else target))

def run_whatweb(docker_client, image, target, command, volume):
    return docker_client.containers.run(image, remove=True, command=command if command else ["--color=never", target])

def run_dirsearch(docker_client, image, target, command, volume):
    return docker_client.containers.run(image, remove=True, command=command if command else ["--no-color", "-q", "-u", target])

def run_subfinder(docker_client, image, target, command, volume):
    return docker_client.containers.run(image, remove=True, command=command if command else ["-d", target])

def run_naabu(docker_client, image, target, command, volume):
    if volume:
        volume_command = (command if command else []) + ["-list", "/targets.txt"]
        return docker_client.containers.run(image, remove=True, command=volume_command, volumes=volume)
    return docker_client.containers.run(image, remove=True, command=(command + ["-host", target] if command else ["-host", target]))

def run_httpx(docker_client, image, target, command, volume):
    return docker_client.containers.run(image, remove=True, command=command if command else ["-u", target])

def run_nuclei(docker_client, image, target, command, volume):
    return docker_client.containers.run(image, remove=True, command=command if command else ["-u", target])

def run_container(image, docker_client, target, command, volume):
    print(f"[+] Running container {str(image.capitalize())} with target file: {Path(volume[0].split(':')[0]).name}" if volume else f"[+] Running container {str(image.capitalize())} on target {str(target)}")
    try:
        if image == "nmap":
            container_output = run_nmap(docker_client, image, target, command, volume)
        elif image == "nmap-small":
            container_output = run_nmap_small(docker_client, image, target, command, volume)
        elif image == "whatweb":
            container_output = run_whatweb(docker_client, image, target, command, volume)
        elif image == "dirsearch":
            container_output = run_dirsearch(docker_client, image, target, command, volume)
        elif image == "subfinder":
            container_output = run_subfinder(docker_client, image, target, command, volume)
        elif image == "naabu":
            container_output = run_naabu(docker_client, image, target, command, volume)
        elif image == "httpx":
            container_output = run_httpx(docker_client, image, target, command, volume)
        elif image == "nuclei":
            container_output = run_nuclei(docker_client, image, target, command, volume)
        else:
            raise ValueError(f"Unsupported image: {image}")
        return container_output
    except docker.errors.ContainerError as e:
        print(f"[-] Container error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        sys.exit(1)
