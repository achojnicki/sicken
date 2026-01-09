#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
nc='\033[0m'
bold='\033[1m'

run() {
	prompt_char='$'
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


print 'Installing Sicken...'
run cd /opt/sicken

print "Updating \$PATH"
export PATH=$PATH:/usr/local/bin:/usr/local/sbin:/opt/sicken/install


print "1st stage installation of dependencies"
run "brew install python@3.12 ollama ffmpeg"

print "2nd stage installation of dependencies"
run "/usr/local/bin/python3.12 -m pip install --break-system-packages numpy eventlet openai pydub flask flask-socketio python-socketio psutil tabulate colored pymongo pyyaml pika uwsgi websockets pyobjc twitchapi wxpython ollama"


print "Installing MongoDB database"
run "brew tap mongodb/brew"
run "brew update"
run "brew install mongodb-community@8.0"

run "brew services"

run "brew services start mongodb-community"

print "Installing RabbitMQ"
run "brew install rabbitmq"
run "brew services start rabbitmq"
run "sleep 10"



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
run '/usr/local/bin/python3.12 create_queue.py sicken-events'
run '/usr/local/bin/python3.12 create_queue.py sicken-logs'
run '/usr/local/bin/python3.12 create_queue.py sicken-response_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-speech_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-vtube_plugin_load_model_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-vtube_plugin_speech_generation_finished'
run '/usr/local/bin/python3.12 create_queue.py sicken-vtube_plugin_speech_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-standalone_speech_generation_finished'
run '/usr/local/bin/python3.12 create_queue.py sicken-standalone_speech_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-model_introduction'
run '/usr/local/bin/python3.12 create_queue.py sicken-model_introduction_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-gui_responses'
run '/usr/local/bin/python3.12 create_queue.py sicken-twitch_responses'
run '/usr/local/bin/python3.12 create_queue.py sicken-gui_logs'
run '/usr/local/bin/python3.12 create_queue.py sicken-webchat_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-webchat_responses'
run '/usr/local/bin/python3.12 create_queue.py sicken-subtitles'
run '/usr/local/bin/python3.12 create_queue.py sicken-classification_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-command_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-command_feedback'
run '/usr/local/bin/python3.12 create_queue.py sicken-gui_commands_feedback'
run '/usr/local/bin/python3.12 create_queue.py sicken-agent_command_execution_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-agent_command_execution_response'
run '/usr/local/bin/python3.12 create_queue.py sicken-agent_spawn_proceses_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-agent_terminal_characters_requests'
run '/usr/local/bin/python3.12 create_queue.py sicken-agent_terminal_snapshot_response'

print "Enable RabbitMQ Managment plugin"
run "rabbitmq-plugins enable rabbitmq_management"

#print "Pulling Gemma3:4b model(may take a while)"
#ollama pull gemma3:4b

run "mkdir /opt/sicken/logs"
run "mkdir /opt/sicken/files"
run "mkdir /opt/sicken/files/sicken"
run "mkdir /opt/sicken/files/sicken/speech"
run "chmod 775 /opt/sicken/files/sicken/speech"
run "touch /opt/sicken/logs/sicken-concurrent.log"
run "chmod 775 /opt/sicken/logs/sicken-concurrent.log"

print "Installation complete"   