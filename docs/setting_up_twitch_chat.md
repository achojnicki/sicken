# Setting up Twitch Chat.

## Introduction

To set up Sicken to work with the Twitch chat you'll need:

* VTube Studio installed on the machine
* Sicken installed on the machine
* Twitch account with a Two-Factor verification enabled
* Twitch app created at [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)


## Setup

1. Go to the [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps) and register the new APP with the settings below.

	Settings:

	| Field                       | Value                                   |
	| ----------------------------| --------------------------------------- |
	| Name                        | Name for your app(must be unique)       |
	| OAuth Redirect URLs         | http://localhost:17563                  |
	| Category                    | Chat Bot                                |
	| Client Type                 | Confidential                            |


2. After creating a new application, go to manage, copy the **Client Id** and place this value in the `/opt/sicken/configs/sicken-twitch_chat.yaml` file under the `client_id` value in the `twitch` tree.

3. The next step is to generate the **Secret Key** in Twitch's application management. After generating the `Secret Key`, go to the `/opt/sicken/configs/sicken-twitch_chat.yaml` config file and replace the `secret_key` value of the `twitch` tree with the copied secret key.

4. In the file `/opt/sicken/configs/sicken-twitch_chat.yaml`, change the `channel` value of the `twitch` tree to your Twitch **username** - this way the twitch integration will be able to connect to your stream's chat. 

5. Configuration is ready. To start the Twitch chat integration simply run it on Mac:
	```
	python3.12 /opt/sicken/workers/sicken-twitch_chat
	```

	on Linux:
	```
	python3 /opt/sicken/workers/sicken-twitch_chat
	```

	Starting this command will invoke the browser window with Twitch authorisation. You must to authorise the APP to be used with your Twitch account. 

> [!NOTE]
>
> Sicken's Concurrent must be running parallelly to the Sicken's Twitch chat integration

> [!NOTE]
>
> VTube Studio must be on and running before starting Sicken's Concurrent
