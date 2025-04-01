# Tacticontainer

An automation tool for running Red Team tools in containers

Tacticontainer (a play off [Tacticooler](https://splatoon.fandom.com/wiki/Tacticooler), a sub-weapon in the video game Splatoon) uses the Docker SDK for Python to automate the running of Red Team tools in containers. The outputs are written to organized files.

![alt text](.img/tacticooler.png)

The [Arsenal-containers](https://github.com/sneakerhax/Arsenal-containers) repo is pulled when the tool runs and remote sources are supported.

## Install Docker

Docker is required to run the containers.

* [Get Docker](https://docs.docker.com/get-docker/)

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

## Using terminal for development or install (Requires python3-venv and python3-pip)

```
apt install python3-venv python3-pip
```

Install Python3 Virtual Environments and Python3 pip

```
python3 -m venv .venv
```

Create virtual environment (from Tacticontainer root folder)

```
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
python3 tacticontainer.py -n <name_of_target> -t <target> -i <docker_image_name>
```

## Available Options
```
--name            Name of target (this will become the output folder name)
--target          Target the tool will run on
--image           The name of the image that will run
```

## Example Usage

```
$ python3 tacticontainer.py -n sample -t scanme.nmap.org -i nmap
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
Running basic nmap scan with required arguments

```
$ python3 tacticontainer.py -n scanme -t scanme.nmap.org -i naabu -c "-p 80 -j -host scanme.nmap.org"
  ______           __  _                  __        _
 /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____
  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/
 / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /
/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__/\__,_/_/_/ /_/\___/_/

         by sneakerhax...

[+] Pulling Arsenal-containers Github repo
[+] Pulling Naabu Github repo
[+] Building image Naabu
[*] Starting Scan at 02-11-2025_17:57:52
[+] Running container Naabu on target scanme.nmap.org
[*] Finished Scan at 02-11-2025_17:57:55
[+] Writing output to output/scanme/scanme.nmap.org_naabu_02-11-2025_17:57:55.txt
```
When using -c you must specify all arguments and the target (Unless specifying target file)

```
python3 tacticontainer.py -i nmap -n scanme.nmap.org -f targets.txt           
  ______           __  _                  __        _
 /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____
  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/
 / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /
/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__/\__,_/_/_/ /_/\___/_/

         by sneakerhax...

[+] Pulling Arsenal-containers Github repo
[+] Building image Nmap
[*] Starting Scan at 03-25-2025_18:01:01
[+] Running container Nmap with target file: targets.txt
[*] Finished Scan at 03-25-2025_18:01:02
[+] Writing output to output/scanme.nmap.org/nmap_03-25-2025_18:01:02.txt
```

Running scan with target file

## Current images

* Nmap (supports target file)
* Nmap-small
* Whatweb
* Dirsearch
* Subfinder
* Naabu
* Httpx
* Nuclei

## References

* [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/)
