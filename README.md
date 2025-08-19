# Tacticontainer

Automation for running Red Team tools in containers

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-FADA5E.svg?logo=python)](https://www.python.org/) [![golang](https://img.shields.io/badge/golang-1.17+-29BEB0.svg?logo=GO)](https://go.dev/)
[![Docker](https://img.shields.io/badge/docker-required-0db7ed.svg?logo=docker)](https://www.docker.com/) [![PEP8](https://img.shields.io/badge/code%20style-pep8-red.svg)](https://www.python.org/dev/peps/pep-0008/) [![License](https://img.shields.io/badge/license-GPL3-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) [![Twitter](https://img.shields.io/badge/twitter-sneakerhax-38A1F3?logo=twitter)](https://twitter.com/sneakerhax)


Tacticontainer (a play on [Tacticooler](https://splatoon.fandom.com/wiki/Tacticooler), a sub-weapon in the video game Splatoon) uses the Docker SDK for Python to automate the running of Red Team tools in containers. The outputs are written to organized files.

![alt text](.img/tacticooler.png)

The [Containers](https://github.com/sneakerhax/Containers) repo is pulled when the tool runs and remote sources are supported.

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

## Basic Usage

```zsh
python3 tacticontainer.py -n <name_of_output_folder> -t <target> -i <docker_image_name>
```

## Available Options
```
-n, --name            Name of output folder
-t, --target          The target to run the tool on
-i, --image           The name of the image to run
-f, --file            The targets file location
-c, --command.        Custom command to run (space-separated arguments)
-d, --debug           Debug mode
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

[+] Pulling Containers Github repo
[+] Pulling Naabu Github repo
[+] Building image Naabu
[*] Starting Scan at 02-11-2025_17:57:52
[+] Running container Naabu on target scanme.nmap.org
[*] Finished Scan at 02-11-2025_17:57:55
[+] Writing output to output/scanme/scanme.nmap.org_naabu_02-11-2025_17:57:55.txt
```
When using -c you must specify all arguments and the target (Unless specifying targets file)

```
python3 tacticontainer.py -i nmap -n scanme.nmap.org -f targets.txt           
  ______           __  _                  __        _
 /_  __/___ ______/ /_(_)________  ____  / /_____ _(_)___  ___  _____
  / / / __ `/ ___/ __/ / ___/ __ \/ __ \/ __/ __ `/ / __ \/ _ \/ ___/
 / / / /_/ / /__/ /_/ / /__/ /_/ / / / / /_/ /_/ / / / / /  __/ /
/_/  \__,_/\___/\__/_/\___/\____/_/ /_/\__/\__,_/_/_/ /_/\___/_/

         by sneakerhax...

[+] Pulling Containers Github repo
[+] Building image Nmap
[*] Starting Scan at 03-25-2025_18:01:01
[+] Running container Nmap with target file: targets.txt
[*] Finished Scan at 03-25-2025_18:01:02
[+] Writing output to output/scanme.nmap.org/nmap_03-25-2025_18:01:02.txt
```

Running an nmap scan with targets file

## Supported Images

| Image      | Remote Source | Custom Command | Target File |
|:-----------|:--------------|:---------------|:------------|
| Nmap       | No            | Yes            | Yes         |
| Nmap-small | No            | Yes            | No          |
| Whatweb    | No            | Yes            | No          |
| Dirsearch  | Yes           | Yes            | No          |
| Subfinder  | Yes           | Yes            | No          |
| Naabu      | Yes           | Yes            | No          |
| HTTPX      | Yes           | Yes            | No          |
| Nuclei     | Yes           | Yes            | No          |


## References

* [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/)
