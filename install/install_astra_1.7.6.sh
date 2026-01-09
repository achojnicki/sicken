#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
nc='\033[0m'
bold='\033[1m'

run() {
	prompt_char='#'
	command=$*
	echo $prompt_char $command
	output=`$* 2>&1`
	exit_code=$?
	
	if [ $exit_code != 0 ] 
	then 
		echo Output: $output
  		echo -e Status: ${red}Failed${nc}
  	else
  		echo -e Status: ${green}Success${nc}
	fi
}

print() {
echo -e ${bold}$*${nc}	
}

logo() {
cat <<"EOF"
 ____ ___ ____ _  _______ _   _ 
/ ___|_ _/ ___| |/ / ____| \ | |
\___ \| | |   | ' /|  _| |  \| |
 ___) | | |___| . \| |___| |\  |
|____/___\____|_|\_\_____|_| \_|

EOF
}

logo

if [ "$EUID" -ne 0 ]
  then 
  	print "This script must be run as root. Exitting"
  exit
fi

print 'Installing Sicken...'
run cd /opt/sicken

print "Updating \$PATH"
export PATH=$PATH:/sbin:/usr/sbin:/usr/local/sbin:/opt/sicken/install

print "Updating local APT cache"
run "apt-get update"

print "1st stage installation of dependencies(may take a while)"
run "apt-get install curl gnupg apt-transport-https python3.11 python3-pip curl dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3-dev libsm-dev libgtk-3-dev libwebkit2gtk-4.0-dev libxtst-dev libsdl2-dev ffmpeg -y"

print 'Downloading and installing modern pip3'
run 'curl -sSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py'
run 'python3.11 /tmp/get-pip.py'

print "2nd stage installation of dependencies(may take a while)"
run "python3.11 -m pip install numpy openai pydub flask flask-socketio python-socketio psutil tabulate colored pymongo eventlet pyyaml pika uwsgi websockets twitchapi wxpython"


print "Downloading and instaling MongoDB key"
curl -fsSL https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -

print "Adding MongoDB APT repository"
sudo add-apt-repository 'deb https://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main'


print "Updating local APT cache"
run "apt-get update"

print "Installing MongoDB database"
run "apt-get install -y mongodb-org"

print "Enabling MongoDB service"
run "systemctl enable mongod.service"

print "Staring MongoDB service"
run "service mongod start"

print "Installing Erlang"
run "apt-get install -y erlang-base erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key erlang-runtime-tools erlang-snmp erlang-ssl erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl"

print "Installing RabbitMQ"
run "apt-get install rabbitmq-server -y --fix-missing"

print "Creating RabbitMQ users"
run "rabbitmqctl delete_user guest"
run "rabbitmqctl add_user sicken-logs password"
run "rabbitmqctl add_user sicken-events password"
run "rabbitmqctl add_user sicken-openai_llm password"
run "rabbitmqctl add_user sicken-speech_generator password"
run "rabbitmqctl add_user sicken-text_input password"
run "rabbitmqctl add_user sicken-microphone_input password"
run "rabbitmqctl add_user sicken-vtube_plugin password"
run "rabbitmqctl add_user sicken-twitch_chat password"
run "rabbitmqctl add_user sicken-gui password"
run "rabbitmqctl add_user sicken-ollama_llm password"
run "rabbitmqctl add_user sicken-deepseek_llm password"
run "rabbitmqctl add_user sicken-grok_llm password"
run "rabbitmqctl add_user sicken-classification password"
run "rabbitmqctl add_user sicken-chat_viewer password"
run "rabbitmqctl add_user sicken-bottom_bar password"
run "rabbitmqctl add_user sicken-tiktok_chat password"
run "rabbitmqctl add_user sicken-commands password"


run "rabbitmqctl add_user admin sicken"


print "Setting RabbitMQ users permissions"
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / sicken-logs ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-events ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-openai_llm ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-speech_generator ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-text_input ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-microphone_input ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-vtube_plugin ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-ollama_llm ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-deepseek_llm ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-grok_llm ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-twitch_chat ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-gui ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-classification ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-chat_viewer ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-bottom_bar ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-tiktok_chat ".*" ".*" ".*"
rabbitmqctl set_permissions -p / sicken-commands ".*" ".*" ".*"
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

rabbitmqctl set_topic_permissions sicken-logs "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-events "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-openai_llm "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-speech_generator "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-text_input "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-microphone_input "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-vtube_plugin "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-ollama_llm "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-deepseek_llm "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-grok_llm "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-twitch_chat "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-gui "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-classification "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-chat_viewer "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-bottom_bar "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-tiktok_chat "" ".*" ".*"
rabbitmqctl set_topic_permissions sicken-commands "" ".*" ".*"
rabbitmqctl set_topic_permissions admin "" ".*" ".*"

print 'Creating RabbitMQ Queues'
run 'python3.11 ./create_queue_astra.py sicken-events'
run 'python3.11 ./create_queue_astra.py sicken-logs'
run 'python3.11 ./create_queue_astra.py sicken-response_requests'
run 'python3.11 ./create_queue_astra.py sicken-speech_requests'
run 'python3.11 ./create_queue_astra.py sicken-vtube_plugin_speech_generation_finished'
run 'python3.11 ./create_queue_astra.py sicken-vtube_plugin_speech_requests'
run 'python3.11 ./create_queue_astra.py sicken-vtube_plugin_load_model_requests'
run 'python3.11 ./create_queue_astra.py sicken-standalone_speech_generation_finished'
run 'python3.11 ./create_queue_astra.py sicken-standalone_speech_requests'
run 'python3.11 ./create_queue_astra.py sicken-model_introduction'
run 'python3.11 ./create_queue_astra.py sicken-model_introduction_requests'
run 'python3.11 ./create_queue_astra.py sicken-gui_responses'
run 'python3.11 ./create_queue_astra.py sicken-twitch_responses'
run 'python3.11 ./create_queue_astra.py sicken-gui_logs'
run 'python3.11 ./create_queue_astra.py sicken-webchat_requests'
run 'python3.11 ./create_queue_astra.py sicken-webchat_responses'
run 'python3.11 ./create_queue_astra.py sicken-subtitles'
run 'python3.11 ./create_queue_astra.py sicken-classification_requests'
run 'python3.11 ./create_queue_astra.py sicken-command_requests'
run 'python3.11 ./create_queue_astra.py sicken-command_feedback'
run 'python3.11 ./create_queue_astra.py sicken-gui_commands_feedback'
run 'python3.11 ./create_queue_astra.py sicken-agent_command_execution_requests'
run 'python3.11 ./create_queue_astra.py sicken-agent_command_execution_response'
run 'python3.11 ./create_queue_astra.py sicken-agent_spawn_proceses_requests'
run 'python3.11 ./create_queue_astra.py sicken-agent_terminal_characters_requests'
run 'python3.11 ./create_queue_astra.py sicken-agent_terminal_snapshot_response'




print "Enable RabbitMQ Managment plugin"
run "rabbitmq-plugins enable rabbitmq_management"

#print "Installing Ollama"
#curl -fsSL https://ollama.com/install.sh | sh

#print "Pulling Gemma3:4b model(may take a while)"
#ollama pull gemma3:4b


#print "Installing Sicken Nginx sites"
#run "ln -s /opt/adistools/nginx_sites/* /etc/nginx/sites-enabled/"

#print "Restarting NGINX"
#run "service nginx restart"

#print "Adding adistools service"
#run "ln -s /opt/adistools/systemd/sicken.service /lib/systemd/system/"

#print "Reloading daemons database"
#run "systemctl daemon-reload"

#print "Enable adistools service"
#run "systemctl enable sicken.service"

#print "Start adistools daemon"
#run "service adistools start"

run "mkdir /opt/sicken/logs"
run "mkdir /opt/sicken/files"
run "mkdir /opt/sicken/files/sicken"
run "mkdir /opt/sicken/files/sicken/speech"
run "chmod -R 755 /opt/sicken/bin "
run "touch /opt/sicken/logs/sicken-concurrent.log"
run "chmod 664 /opt/sicken/logs/sicken-concurrent.log"

print "Installation complete"   