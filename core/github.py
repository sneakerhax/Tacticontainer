
from pathlib import Path
from git import Repo


def pull_containers_repo(containers_dir):
    """Pull or clone the main Containers GitHub repository."""
    if Path.exists(Path(containers_dir)):
        print("[+] Pulling Containers GitHub repo")
        repo = Repo(containers_dir)
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("[+] Cloning Containers GitHub repo")
        Repo.clone_from("https://github.com/sneakerhax/Containers", containers_dir)


def pull_remote_source(image, tool_dir, remote_repo):
    """Pull or clone a remote tool's GitHub repository."""
    if Path.exists(Path(tool_dir)):
        print(f"[+] Pulling {image.capitalize()} GitHub repo")
        repo = Repo(tool_dir)
        origin = repo.remotes.origin
        origin.pull()
    else:
        print(f"[+] Cloning {image.capitalize()} GitHub repo")
        Repo.clone_from(remote_repo, tool_dir)
