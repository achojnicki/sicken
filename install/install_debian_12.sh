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
export PATH=$PATH:/sbin:/usr/sbin:/usr/local/sbin

print "Updating local APT cache"
run "apt-get update"

print "1st stage installation of dependencies"
run "apt-get install curl gnupg apt-transport-https nmap python3 python3-pip nginx curl -y"

print "2nd stage installation of dependencies"
run "pip3 install --break-system-packages flask flask-socketio python-socketio psutil tabulate colored pymongo pyyaml pika uwsgi websockets"

print "Downloading and instaling MongoDB key"
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg

print "Adding MongoDB APT repository"
echo  "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list >/dev/null

print "Updating local APT cache"
run "apt-get update"

print "Installing MongoDB database"
run "apt-get install -y mongodb-org"

print "Enabling MongoDB service"
run "systemctl enable mongod.service"

print "Staring MongoDB service"
run "service mongod start"

print "Downloading and installing RabbitMQ main signing key"
curl -1sLf 'https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA' | gpg --dearmor | tee /usr/share/keyrings/com.rabbitmq.team.gpg >/dev/null

print "Downloading and installing RabbitMQ 2nd key"
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-erlang.E495BB49CC4BBE5B.key | gpg --dearmor | tee /usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg >/dev/null

print "Downloading and installing RabbitMQ 3rd key"
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-server.9F4587F226208342.key | gpg --dearmor | tee /usr/share/keyrings/rabbitmq.9F4587F226208342.gpg> /dev/null

print "Installing Erlang and RabbitmMQ Repositories"
tee /etc/apt/sources.list.d/rabbitmq.list >/dev/null <<EOF
## Provides modern Erlang/OTP releases
##
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/debian bookworm main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/debian bookworm main

# another mirror for redundancy
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/debian bookworm main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/debian bookworm main

## Provides RabbitMQ
##
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-server/deb/debian bookworm main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-server/deb/debian bookworm main

# another mirror for redundancy
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-server/deb/debian bookworm main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-server/deb/debian bookworm main
EOF

print "Updating local APT cache"
run "apt-get update"

print "Installing Erlang"
run "apt-get install -y erlang-base erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key erlang-runtime-tools erlang-snmp erlang-ssl erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl"

print "Installing RabbitMQ"
run "apt-get install rabbitmq-server -y --fix-missing"

print "Creating RabbitMQ users"
run "rabbitmqctl add_user sicken-logs password"
run "rabbitmqctl add_user sicken-events password"
run "rabbitmqctl add_user sicken-openai_llm password"
run "rabbitmqctl add_user sicken-speech_generator password"
run "rabbitmqctl add_user sicken-text_input password"
run "rabbitmqctl add_user sicken-microphone_input password"
run "rabbitmqctl add_user sicken-vtube_plugin password"
run "rabbitmqctl add_user admin sicken"


print "Setting RabbitMQ users permissions"
run "rabbitmqctl set_user_tags admin administrator"
run "rabbitmqctl set_permissions -p / sicken-logs '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-events '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-openai_llm '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-speech_generator '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-text_input '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-microphone_input '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-vtube_plugin '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / sicken-openai_llm '.*' '.*' '.*'"
run "rabbitmqctl set_permissions -p / admin '.*' '.*' '.*'"

run "rabbitmqctl set_topic_permissions sicken-logs '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-events '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-openai_llm '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-speech_generator '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-text_input '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-microphone_input '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-vtube_plugin '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions sicken-openai_llm '' '.*'' '.*'"
run "rabbitmqctl set_topic_permissions admin '' '.*'' '.*'"






print "Enable RabbitMQ Managment plugin"
run "rabbitmq-plugins enable rabbitmq_management"

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
run "touch /opt/sicken/logs/sicken-concurrent.log"
run "chmod 777 /opt/sicken/logs/sicken-concurrent.log"

print "Installation complete"   