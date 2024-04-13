# Tacticontainer

An automation tool for running Offensive Security tools in containers

Tacticontainer (a play off [Tacticooler](https://splatoon.fandom.com/wiki/Tacticooler), a sub-weapon in the video game Splatoon) uses the Docker SDK for Python to automate the running of Offensive Security tools in containers. The outputs are written to organized files.

![alt text](.img/tacticooler.png)

The [Arsenal-containers](https://github.com/sneakerhax/Arsenal-containers) repo is pulled when the tool runs and remote sources are supported.

## Install Docker

Docker is required to run the containers.

* <https://docs.docker.com/get-docker/>

## Install Docker SDK for Python

```zsh
python3 -m pip install -r requirements.txt
```

## Using VS Code for development

```zsh
shift + command (⌘) + P -> Python: Create Environment
```

Creates a new environment after following the instructions (all dependencies should be added automatically)

* [Python Environments in VS Code](https://code.visualstudio.com/docs/python/environments)

```zsh
source .venv/bin/activate
```

Activate environment


## Adding keys to the config file

Keys should be added to config.conf (Example for Censys):

```zsh
[censys.io]
censys_API_ID = <censys_API_ID>
censys_secret = <censys_secret>
```

## Usage

```zsh
python3 tacticontainer -n <name_of_target> -t <target> -i <docker_image_name>
```

## Available Options
```
--name            Name of target (this will become the output folder name)
--target          Target the tool will run on
--image           The name of the image that will run
```

## Example Usage

```
$ tacticontainer $ python3 tacticontainer.py -n sample -t scanme.nmap.org -i nmap
  ______           __  _                  __        _
 /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____
  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/
 / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /
/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__/\__,_/_/_/ /_/\___/_/

	 by sneakerhax...

[+] Building image nmap
[*] Starting Scan at 11-03-2021_13:34:35
[+] Running container nmap on target scanme.nmap.org
[*] Finished Scan at 11-03-2021_13:34:38
[+] Writing output to output/10.0.0.1/scanme.nmap.org_nmap_11-03-2021_13:34:38.txt
```

## Current images

* Nmap
* Nmap-small
* PyDNSRecon (Deprecated)
* PyDNSRecon-Passive (Deprecated)
* PyDNSRecon-m1 (Deprecated)
* Whatweb
* Dirsearch
* Subfinder

## References

* <https://docker-py.readthedocs.io/en/stable/>
