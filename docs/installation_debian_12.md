# Installation on Debian 12

## Introduction

To install and operate Sicken on the Debian Bookworm machine, you'll need:

* An AMD64 machine with Debian Bookworm installed
* Steam instance and VTube Studio installed
* An account and credits at one(or more) of supported AI services providers(OpenAI, XAI, DeepSeek)

## Installation

1. **Install `git` and clone Sicken Git Repository to the `/opt` directory.**
	```
	$ su
	# apt install git
	# cd /opt
	# git clone https://github.com/achojnicki/sicken.git
	# exit
	```

2. **Execute the Sicken's installation script and wait until the installer finishes installation of all required dependencies.**
	```
	$ su
	# cd /opt/sicken/install
	# bash ./install_debian_12.sh
	# exit
	```

3. **Populate API Keys of desired provider(s). If you decide to use an AI provider other than OpanAI, you will also need to provide the API Key for OpenAI as well, as the speech generation and classification of memories rely on the OpenAI.**

	Files to modify to populate API Keys:

	* OpenAI
		- `/opt/sicken/configs/sicken-openai_llm.yaml`
		- `/opt/sicken/configs/sicken-classification.yaml`
		- `/opt/sicken/configs/sicken-speech-generator.yaml`
	* XAI
		- `/opt/sicken/configs/sicken-grok_llm.yaml`
	* DeepSeek
		- `/opt/sicken/configs/sicken-deepseek_llm.yaml`

4. **Enable the desired worker of the AI services and disable all others.**

	Sicken is designed using modular architecture, which allows to replace the workers responsible to perform required task as long as it uses the same data structure for communication. In this case, there is number of the workers responsible for generating answers of Sicken using external AI services. To choose the desired one is to enable the worker of the desired service in the `/opt/sicken/configs/sicken-concurrent_workers.yaml` and disable all others.

	For example, if you want to use an OpenAI to generate Sicken's answers, you need to enable the worker `sicken-openai_llm` in the `/opt/sicken/configs/sicken-concurrent_workers.yaml` and disable all other workers with the `llm` suffix. To achieve this, you need to change the `enable` key of the desired worker to `true` and all other workers with the `llm` suffix to `false`.

	An example of the `/opt/sicken/configs/sicken-concurrent_workers.yaml` file configured to use the OpenAI service:
	
	```
	sicken-log_worker:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-events:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-openai_llm:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-deepseek_llm:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-grok_llm:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-ollama_llm:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-speech_generator:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-vtube_plugin:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-gui:
	  enable: true
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-classification:
	  enable: true
	  workers_count: 5
	  uid: 7676
	  gid: 7676

	sicken-twitch_chat:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-chat_viewer:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676

	sicken-bottom_bar:
	  enable: false
	  workers_count: 1
	  uid: 7676
	  gid: 7676
	```
5. **Populating the Sicken's memories classifications to the database.**

	To populate the Sicken's memories classifications, you'll need to execute the `load_classifications.py` file present in the `/opt/sicken/tools` directory.

	```
	$ python3 /opt/sicken/tools/load_classifications.py
	```


6. **Installation is complete. To start Sicken, simply type in the terminal `python3 /opt/sicken`.**

> [!NOTE]
> 
> VTube Studio must be up and running before starting sicken-concurrent.