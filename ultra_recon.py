import argparse
import configparser
import datetime
import docker
import sys
from git import Repo
from os import system
from pathlib import Path
from urllib.parse import urlparse


# global variables
containers_dir = "Arsenal-containers"


def banner():
    print("    __  ______                ____")
    print("   / / / / / /__________ _   / __ \___  _________  ____")
    print("  / / / / / __/ ___/ __ `/  / /_/ / _ \/ ___/ __ \/ __ \\")
    print(" / /_/ / / /_/ /  / /_/ /  / _, _/  __/ /__/ /_/ / / / /")
    print(" \____/_/\__/_/   \__,_/  /_/ |_|\___/\___/\____/_/ /_/")
    print("")
    print("\t by sneakerhax...")
    print("")


# Check if arsenal containers directory exists. If true update if false clone.
def pull_arsenal_containers():
    if Path.exists(Path(containers_dir)):
        print("[+] Pulling Arsenal-containers Github repo")
        repo = Repo("Arsenal-containers")
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("[+] Cloning Arsenal-containers Github repo")
        Repo.clone_from("https://github.com/sneakerhax/Arsenal-containers", "Arsenal-containers")


# Check if tool directory exists. If true update if false clone.
def pull_remote_source(image, tool_dir):
    if Path.exists(Path(tool_dir)):
        print("[+] Pulling Dirsearch Github repo")
        repo = Repo("Arsenal-containers/Dirsearch")
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("[+] Cloning Dirsearch Github repo")
        Repo.clone_from("https://github.com/maurosoria/dirsearch.git", "Arsenal-containers/Dirsearch")


# Check for image path. If true build image if false exit.
def build_image(docker_client, image, tool_dir):
    print("[+] Building image " + str(image))
    if Path.exists(tool_dir):
        docker_client.images.build(path=str(tool_dir), rm=True, tag=image)
    else:
        print("[-] Path to Dockerfile does not exist")
        sys.exit()


# Extract url based target names by returning target without http:// or https://
# Used for writing to output path
def extract_hostname(target):
    target = urlparse(target).netloc
    return target


# Determine image and run corresponding container run command
def run_container(image, docker_client, target):
    print("[+] Running container " + str(image) + " on target " + str(target))
    if image == "nmap":
        container_output = docker_client.containers.run(image, remove=True, command=target)
    if image == "nmap-small":
        container_output = docker_client.containers.run(image, remove=True, command=target)
    if image == "whatweb":
        container_output = docker_client.containers.run(image, remove=True, command=["--color=never", target])
    if image == "dirsearch":
        container_output = docker_client.containers.run(image, remove=True, command=["--no-color", "-q", "-u", target])
    return container_output


def main():

    # print banner
    banner()

    # parse arguments from command line
    parser = argparse.ArgumentParser(description='Ultra Recon')
    parser.add_argument('-n', '--name', required=True, action='store', dest='name', type=str, help='Target name')
    parser.add_argument('-t', '--target', required=True, action='store', dest='target', type=str, help='Target to scan')
    parser.add_argument('-i', '--image', required=True, action='store', dest='image', type=str, help="Name of Image")
    parser.add_argument('-c', '--command', action='store', dest='command', type=str, help="Command to pass")
    args = parser.parse_args()

    # load configuration file
    try:
        config = configparser.ConfigParser()
        config.read('config.conf')
        # censys_API_ID = config['censys.io']['censys_API_ID']
        # censys_secret = config['censys.io']['censys_secret']
    except Exception as e:
        print("[-] Failed to load config file")

    # pull or update arsenal containers folder
    pull_arsenal_containers()

    image = args.image
    target = args.target

    # Set tool dirctory
    tool_dir = Path('Arsenal-containers', image)

    # Connect to the Docker daemon
    try:
        docker_client = docker.from_env()
    except Exception as e:
        print("[-] Failed when connecting to Docker daemon")
        sys.exit()

    # Check if image is dirsearch. This function needs to be updated so that it can be used for all remote sources
    if image == "dirsearch":
        pull_remote_source(image, tool_dir)

    # Build Docker image with Docker SDK for Python
    build_image(docker_client, image, tool_dir)

    # Run Docker container with Docker SDK for Python
    now_scan_start = datetime.datetime.now()
    print("[*] Starting Scan at " + now_scan_start.strftime("%m-%d-%Y_%H:%M:%S"))
    container_output = run_container(image, docker_client, target)
    now_scan_end = datetime.datetime.now()
    print("[*] Finished Scan at " + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S"))

    # Target output file check and creation
    output_dir = Path('output', args.name)
    output_dir.mkdir(exist_ok=True, parents=True)
    # Write container stdout to output folder
    if image == "dirsearch":
        target = extract_hostname(target)
    outputpath = Path(output_dir, target + "_" + image + "_" + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S") + ".txt")
    print("[+] Writing output to " + str(outputpath))
    with open(outputpath, 'w') as out:
        out.write(container_output.decode())


if __name__ == '__main__':
    main()
