# Installing Sicken on MacOS

## Introduction

To install Sicken on a MacOS machine you'll need:

* Intel Mac(Tested on Sonoma and Sequoia)
* Homebrew installed
* Steam account with the VTube Studio installed

## Installation

1. **Download and install Homebrew on your Mac:** [https://brew.sh/](https://brew.sh/)
2. **Clone Sicken's Git Repository to the /opt/sicken directory**.

	```
 	sudo bash
	cd /opt/
	git clone https://github.com/achojnicki/sicken.git
 	exit
 	sudo chown -R "$USER":admin /opt/sicken
	```
3. **Run installation script**
	```
	cd /opt/sicken/install
	bash ./install_macos.sh
	```
4. **Modify manifest files to run the subprocesses with the right Python interpreter**.
	Files to modify:

	* /opt/sicken/sicken-events/manifest.yaml
	* /opt/sicken/sicken-log_worker/manifest.yaml
	* /opt/sicken/sicken-openai_llm/manifest.yaml
	* /opt/sicken/sicken-speech_generator/manifest.yaml
	* /opt/sicken/sicken-vtube_plugin/manifest.yaml
	* /opt/sicken/sicken-gui/manifest.yaml

	The Modification requires changing the `exec` property from `/usr/bin/python3` to `/usr/local/bin/python3.12` in every manifest file mentioned.
	
	Before:
	```
	name: sicken-events
	exec: /usr/bin/python3
	script: __main__.py
	```
	After:  
	```
	name: sicken-events
	exec: /usr/local/bin/python3.12
	script: __main__.py
	```

5. **Populate an OpenAI API key in the config files.**  

	Files to modify: 

	* /opt/sicken/configs/sicken-openai_llm.yaml
	* /opt/sicken/configs/sicken-speech_generator.yaml
	* /opt/sicken/configs/sicken-microphone_input.yaml

	The modification requires changing the `api_key` property of the `openai` tree to your API key obtained from [https://platform.openai.com](https://platform.openai.com)

6. **Installation is complete. To start Sicken run in the terminal:**
	```
	python3.12 /opt/sicken
	```