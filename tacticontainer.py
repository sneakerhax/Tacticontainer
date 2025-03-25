import argparse
import configparser
import datetime
import docker
import sys
from git import Repo
from pathlib import Path
from urllib.parse import urlparse


# global variables
containers_dir = "Arsenal-containers"
# remote sources list
remote_sources = [
                ["dirsearch", "https://github.com/maurosoria/dirsearch"], 
                ["subfinder", "https://github.com/projectdiscovery/subfinder"],
                ["naabu", "https://github.com/projectdiscovery/naabu"],
                ["httpx", "https://github.com/projectdiscovery/httpx"]
                ]

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
def run_container(image, docker_client, target, command=[]):
    print("[+] Running container " + str(image.capitalize()) + " on target " + str(target))
    if image == "nmap":
        if command:
            container_output = docker_client.containers.run(image, remove=True, command=command)
        else:
            container_output = docker_client.containers.run(image, remove=True, command=target)
    if image == "nmap-small":
        if command:
            container_output = docker_client.containers.run(image, remove=True, command=command)
        else:
            container_output = docker_client.containers.run(image, remove=True, command=target)
    if image == "whatweb":
        container_output = docker_client.containers.run(image, remove=True, command=["--color=never", target])
    if image == "dirsearch":
        container_output = docker_client.containers.run(image, remove=True, command=["--no-color", "-q", "-u", target])
    if image == "subfinder":
        container_output = docker_client.containers.run(image, remove=True, command=["-d", target])
    if image == "naabu":
        if command:
            container_output = docker_client.containers.run(image, remove=True, command=command)
        else:
            container_output = docker_client.containers.run(image, remove=True, command=["-host", target])
    if image == "httpx":
        if command:
            container_output = docker_client.containers.run(image, remove=True, command=command)
        else:
            container_output = docker_client.containers.run(image, remove=True, command=["-u", target])
    return container_output


def main():

    # print banner
    banner()

    # parse arguments from command line
    parser = argparse.ArgumentParser(description='An automation tool for running Offensive Security tools in containers')
    parser.add_argument('-n', '--name', required=True, action='store', dest='name', type=str, help='Target name')
    parser.add_argument('-t', '--target', required=True, action='store', dest='target', type=str, help='Target to scan')
    parser.add_argument('-i', '--image', required=True, action='store', dest='image', type=str, help="Name of Image")
    parser.add_argument('-c', '--command', action='store', dest='command', type=str, help="Command to pass")
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help="Debug mode")
    args = parser.parse_args()

    # Connect to the Docker daemon
    try:
        docker_client = docker.from_env()
    except Exception as _:
        print("[-] Failed when connecting to Docker daemon")
        sys.exit()
    
    # load configuration file
    try:
        config = configparser.ConfigParser()
        config.read('config.conf')
        # censys_API_ID = config['censys.io']['censys_API_ID']
        # censys_secret = config['censys.io']['censys_secret']
    except Exception as _:
        print("[-] Failed to load config file")

    # pull or update arsenal containers folder
    pull_arsenal_containers()

    # set args as single word variables
    image = args.image
    target = args.target
    command = args.command

    # Set tool dirctory
    tool_dir = Path('Arsenal-containers', image.capitalize())

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
    container_output = run_container(image, docker_client, target, command)
    now_scan_end = datetime.datetime.now()
    print("[*] Finished Scan at " + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S"))

    # Target output file check and creation
    output_dir = Path('output', args.name)
    output_dir.mkdir(exist_ok=True, parents=True)
    # Write container stdout to output folder
    if image == "dirsearch":
        target = extract_hostname(target)
    # Debug function to print container output
    if args.debug:
        print("[*] Debug: Printing container output to console")
        print(container_output.decode())
    outputpath = Path(output_dir, target + "_" + image + "_" + now_scan_end.strftime("%m-%d-%Y_%H:%M:%S") + ".txt")
    print("[+] Writing output to " + str(outputpath))
    with open(outputpath, 'w') as out:
        out.write(container_output.decode())


if __name__ == '__main__':
    main()
