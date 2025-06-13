import argparse
import configparser
import datetime
import docker
import sys
from git import Repo
from pathlib import Path
from urllib.parse import urlparse


# global variables
containers_dir = "Containers"
# remote sources list
remote_sources = [
                ["dirsearch", "https://github.com/maurosoria/dirsearch"], 
                ["subfinder", "https://github.com/projectdiscovery/subfinder"],
                ["naabu", "https://github.com/projectdiscovery/naabu"],
                ["httpx", "https://github.com/projectdiscovery/httpx"],
                ["nuclei", "https://github.com/projectdiscovery/nuclei"]
                ]
# list of tools that support target file input
supports_target_file = ["nmap"]

# print banner
# banner generation: https://patorjk.com/software/taag/#p=display&f=Slant&t=Tacticontainer
def banner():
    print(r"  ______           __  _                  __        _")                
    print(r" /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____")
    print(r"  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/")
    print(r" / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /")  
    print(r"/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__/\__,_/_/_/ /_/\___/_/")    
    print("")
    print("\t by sneakerhax...")
    print("")                                                                 


# Check if containers directory exists. If true update if false clone.
def pull_containers_repo():
    if Path.exists(Path(containers_dir)):
        print("[+] Pulling Containers Github repo")
        repo = Repo("Containers")
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("[+] Cloning Containers Github repo")
        Repo.clone_from("https://github.com/sneakerhax/Containers", "Containers")


# Check if tool directory exists. If true pull repo updates if false clone remote repo.
def pull_remote_source(image, tool_dir, remote_repo):
    if Path.exists(Path(tool_dir)):
        print("[+] Pulling " + str(image.capitalize()) + " Github repo")
        repo = Repo(tool_dir)
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("[+] Cloning " + str(image.capitalize()) + " Github repo")
        Repo.clone_from(remote_repo, tool_dir)


# Check for image path. If true build image if false exit.
def build_image(docker_client, image, tool_dir):
    print("[+] Building image " + str(image.capitalize()))
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


# Extract url based target names by returning target without http:// or https://
# Used for writing to output path
def extract_hostname(url):
    hostname = urlparse(url).netloc
    return hostname


# Determine image and run corresponding container run command
def run_container(image, docker_client, target, command, volume):
    if volume:
        print("[+] Running container " + str(image.capitalize()) + " with target file: " + str(Path(volume[0].split(":")[0]).name))
    else:
        print("[+] Running container " + str(image.capitalize()) + " on target " + str(target))
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


def main():

    # print banner
    banner()

    # parse arguments from command line
    parser = argparse.ArgumentParser(description='An automation tool for running Offensive Security tools in containers')
    parser.add_argument('-n', '--name', required=True, action='store', dest='name', type=str, help='Target name')
    parser.add_argument('-i', '--image', required=True, action='store', dest='image', type=str, help="Name of Image")
    parser.add_argument('-c', '--command', action='store', dest='command', type=str, help="Command to pass (space-separated arguments)")
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help="Debug mode")
    
    # Create a mutually exclusive group for target and file
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('-t', '--target', action='store', dest='target', type=str, help='Target to scan')
    target_group.add_argument('-f', '--file', action='store', dest='file', type=str, help="File to pass")
    
    args = parser.parse_args()

    # Connect to the Docker daemon
    try:
        docker_client = docker.from_env()
    except Exception as e:
        print(f"[-] Failed when connecting to Docker daemon: {e}")
        sys.exit(1)
    
    # load configuration file
    try:
        config = configparser.ConfigParser()
        config.read('config.conf')
        # censys_API_ID = config['censys.io']['censys_API_ID']
        # censys_secret = config['censys.io']['censys_secret']
    except Exception as e:
        print(f"[-] Failed to load config file: {e}")
        sys.exit(1)

    # pull or update containers folder
    try:
        pull_containers_repo()
    except Exception as e:
        print(f"[-] Failed to pull/update containers: {e}")
        sys.exit(1)

    # set args as single word variables
    image = args.image
    name = args.name
    target = args.target
    command = args.command.split() if args.command else None
    file = None
    volume = None
    if args.file:
        if image in supports_target_file:
            try:
                file = Path.resolve(Path(args.file))
                volume = [str(file) + ":" + "/targets.txt"]
            except Exception as e:
                print(f"[-] Failed to resolve file path: {e}")
                sys.exit(1)
        else:
            print(f"[-] {image} does not support target file input")
            sys.exit(1)
    # Set tool directory
    tool_dir = Path('Containers', image.capitalize())

    # Check if tool is in the remote sources list. If true pass the remote repo to the pull_remote_source function
    for tool in remote_sources:
        if tool[0] == image:
            remote_repo = tool[1]
            pull_remote_source(image, tool_dir, remote_repo)


    # Build Docker image with Docker SDK for Python
    build_image(docker_client, image, tool_dir)

    # Run Docker container with Docker SDK for Python
    now_scan_start = datetime.datetime.now()
    print("[*] Starting Scan at " + now_scan_start.strftime("%m-%d-%Y_%H:%M:%S"))
    container_output = run_container(image, docker_client, target, command, volume)
    now_scan_end = datetime.datetime.now()
    print("[*] Finished Scan at " + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S"))

    # Target output file check and creation
    output_dir = Path('output', name)
    output_dir.mkdir(exist_ok=True, parents=True)
    # Write container stdout to output folder
    if image == "dirsearch":
        target = extract_hostname(target)
    # Debug function to print container output
    if args.debug:
        print("[*] Debug: Printing container output to console")
        print(container_output.decode())
    
    # Create output path and write to file
    outputpath = Path(output_dir, image + "_" + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S") + ".txt")
    print("[+] Writing output to " + str(outputpath))
    try:
        with open(outputpath, 'w') as out:
            out.write(container_output.decode())
    except IOError as e:
        print(f"[-] Failed to write output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
