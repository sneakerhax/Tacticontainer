import argparse
import configparser
import datetime
import sys
from pathlib import Path
from urllib.parse import urlparse
from core.docker import build_image, run_container, get_docker_client
from core.github import pull_containers_repo, pull_remote_source


containers_dir = "Containers"
remote_sources = [
    ["dirsearch", "https://github.com/maurosoria/dirsearch"],
    ["subfinder", "https://github.com/projectdiscovery/subfinder"],
    ["naabu", "https://github.com/projectdiscovery/naabu"],
    ["httpx", "https://github.com/projectdiscovery/httpx"],
    ["nuclei", "https://github.com/projectdiscovery/nuclei"]
]
supports_target_file = ["nmap"]


def banner():
    """Prints the ASCII art banner for Tacticontainer."""
    print(r"  ______           __  _                  __        _")
    print(r" /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____")
    print(r"  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/")
    print(r" / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /")
    print(r"/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__\/\__,_/_/_/ /_/\___/_/")
    print("")
    print("\t by sneakerhax...")
    print("")


def extract_hostname(url):
    """Extracts the hostname from a URL for output path naming."""
    hostname = urlparse(url).netloc
    return hostname


def main():
    """Main entry point for Tacticontainer CLI."""
    banner()

    parser = argparse.ArgumentParser(
        description='Automation for running Red Team tools in containers'
    )
    parser.add_argument(
        '-n', '--name', required=True, action='store', dest='name', type=str, help='Folder name to save output'
    )
    parser.add_argument(
        '-i', '--image', required=True, action='store', dest='image', type=str, help='Name of Image to run'
    )
    parser.add_argument(
        '-c', '--command', action='store', dest='command', type=str, help='Command to pass (space-separated arguments)'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true', dest='debug', help='Debug mode'
    )

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '-t', '--target', action='store', dest='target', type=str, help='Target to scan'
    )
    target_group.add_argument(
        '-f', '--file', action='store', dest='file', type=str, help='Targets file location'
    )

    args = parser.parse_args()

    docker_client = get_docker_client()

    try:
        config = configparser.ConfigParser()
        config.read('config.conf')
    except Exception as e:
        print(f"[-] Failed to load config file: {e}")
        sys.exit(1)

    try:
        pull_containers_repo(containers_dir)
    except Exception as e:
        print(f"[-] Failed to pull/update containers: {e}")
        sys.exit(1)

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
                volume = [f"{file}:/targets.txt"]
            except Exception as e:
                print(f"[-] Failed to resolve file path: {e}")
                sys.exit(1)
        else:
            print(f"[-] {image} does not support target file input")
            sys.exit(1)

    tool_dir = Path('Containers', image.capitalize())

    for tool in remote_sources:
        if tool[0] == image:
            remote_repo = tool[1]
            pull_remote_source(image, tool_dir, remote_repo)

    build_image(docker_client, image, tool_dir)

    now_scan_start = datetime.datetime.now()
    print(f"[*] Starting Scan at {now_scan_start.strftime('%m-%d-%Y_%H:%M:%S')}")
    container_output = run_container(image, docker_client, target, command, volume)
    now_scan_end = datetime.datetime.now()
    print(f"[*] Finished Scan at {now_scan_end.strftime('%m-%d-%Y_%H:%M:%S')}")

    output_dir = Path('output', name)
    output_dir.mkdir(exist_ok=True, parents=True)
    if image == "dirsearch":
        target = extract_hostname(target)
    if args.debug:
        print("[*] Debug: Printing container output to console")
        print(container_output.decode())

    outputpath = Path(output_dir, f"{image}_{now_scan_end.strftime('%m-%d-%Y_%H:%M:%S')}.txt")
    print(f"[+] Writing output to {outputpath}")
    try:
        with open(outputpath, 'w') as out:
            out.write(container_output.decode())
    except IOError as e:
        print(f"[-] Failed to write output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
