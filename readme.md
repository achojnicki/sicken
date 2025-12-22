# Sicken.ai
<img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken.png?raw=true" width="100%">  
An AI VTuber based on OpenAI, XAI, or DeepSeek.

## Features

👌 **VTube Studio Plugin** - Sicken is made as the VTube Studio Plugin. This Approach allows her to be used for both local entertainment and streaming.  
🧠 **Memories** - Sicken supports remembering information apart from the context chat.  
✌️ **Guestures** - Sicken supports gestures.  
🍎 **Multi Platform** - Sicken is a multi-platform application, supporting all the major PC and Mac platforms.  
📝 **Knowledge Base** - Sicken has a built-in knowledge base system, allowing it to define its knowledge base in a categorised manner.  
🔄️ **Model Template System** - Sicken has a built-in system of templates for models that allows extending the base of the models supported by Sicken by creating two files for each supported model. Generation of model parameters and a list of supported gestures is on a per-model basis.
⚙️ **A VM Agent** - Sicken supports execution of commands in a VM with it's agent installed. Non-interactive commands are supported as well as the interactive ones running through the terminal emulator made especially for the AI(built-in in the agent).
 

## Installation

For installation guides, see the docs directory, or the videos below.

## Usage

To operate Sicken you'll need:

* AMD64 Linux/Intel Mac machine
* VTube Studio installed
* API key for the AI services provider and credits

To start Sicken on Debian Linux, you'll need to run a terminal instance and start the following command:
```
python3 /opt/sicken
```
On Mac:
```
python3.12 /opt/sicken
```
On Windows:
```
py c:\sicken
```

This will start the process manager of Sicken, which starts submodules specified in the `sicken-concurrent_workers.yaml` config file.  

> [!NOTE]
>
> VTube Studio must be on and running before starting Sicken's Concurrent


## Screenshots

<table>
	<tr>
		<td>
			<a href="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_memories_2.png?raw=true"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_memories_2.png?raw=true"></a>
		</td>
		<td>
			<a href="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_cat_ears.png?raw=true"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_cat_ears.png?raw=true"></a>
		</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_log.png?raw=true"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_log.png?raw=true"></a>
		</td>
	</tr>
</table>

## Videos

Below are a few videos of Sicken in action.

<table>
	<tr>
		<td>
			<a href="https://www.youtube.com/watch?v=cwjDW99yS5U"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_memories.png?raw=true"></a>
		</td>
		<td>
			<a href="https://www.youtube.com/watch?v=FZUz16MBOMM"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_windows_installer.png?raw=true"></a>
		</td>
	</tr>
	<tr>
		<td>
			<a href="https://www.youtube.com/watch?v=d4FViSgLyCI"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_debian_installer.png?raw=true"></a>
		</td>
		<td>
			<a href="https://www.youtube.com/watch?v=NF8PHVxOCcE"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_logging_system.png?raw=true"></a>
		</td>
	</tr>
	<tr>
		<td>
			<a href="https://www.youtube.com/watch?v=YxmQ3sJWp4Q"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_mac.png?raw=true"></a>
		</td>
		<td>
			<a href="https://www.youtube.com/watch?v=ABzlS1dK3RY"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_internet_troubleshoot.png?raw=true"></a>
		</td>
	</tr>
	<tr>
		<td>
			<a href="https://www.youtube.com/watch?v=q7B6ed3dzgo"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_commands.png?raw=true"></a>
		</td>
		<td>
			<a href="https://www.youtube.com/watch?v=x8zqPQhl_AY"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_bandwidth.png?raw=true"></a>
		</td>
	</tr>
	<tr>
		<td>
			<a href="https://www.youtube.com/watch?v=1IxvRef8ONg"><img src="https://github.com/achojnicki/sicken/blob/main/docs/img/Sicken_htop.png?raw=true"></a>
		</td>
	</tr>
</table>
