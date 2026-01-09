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


print 'Installing Sicken...'
run cd /c/sicken


print "1st stage installation of dependencies(may take a while)"
run "winget install -e --id Python.Python.3.12 --disable-interactivity --accept-package-agreements --scope machine"
run "winget install -e --id ffmpeg --disable-interactivity --accept-package-agreements --scope machine"

print "2nd stage installation of dependencies(may take a while)"
run "py -3.12 -m pip install --upgrade setuptools wheel"
run "py -3.12 -m pip install --break-system-packages numpy openai eventlet pydub flask flask-socketio python-socketio psutil tabulate colored pymongo pyyaml pika websockets twitchapi wxpython websocket-client"

print "Installing MongoDB database"
run "winget install -e --id MongoDB.Server --disable-interactivity --accept-package-agreements --scope machine"

print "Downloading Erlang"
export user=`whoami`
export erlang_file=/$RANDOM.exe
export loc=/c/Users/$user/AppData/Local/Temp/$erlang_file
curl -o $loc -L "https://github.com/erlang/otp/releases/download/OTP-27.3.3/otp_win64_27.3.3.exe">/dev/null


print "Installing Erlang"
start $loc
echo Press enter after installation is finished
read nothing

print "Downloading RabbitMQ"
export user=`whoami`
export erlang_file=/$RANDOM.exe
export loc=/c/Users/$user/AppData/Local/Temp/$erlang_file
curl -o $loc -L "https://github.com/rabbitmq/rabbitmq-server/releases/download/v4.1.0/rabbitmq-server-4.1.0.exe">/dev/null

print "Installing RabbitMQ"
start $loc
echo Press enter after installation is finished
read nothing


print "Fixing an Erlang cookie problem"
export user=`whoami`
export p=/c/Users/$user/.erlang.cookie
rm -f $p
echo "Open a Windows File Explorer and navigate to the folder C:\\Windows\\System32\\config\\systemprofile. Next copy the .erlang.cookie file to your profile folder(C:\\Users\\Adrian for user named Adrian.)"
read nothing
echo "press enter after operation is finished"



run "mkdir /c/sicken/logs"
run "mkdir /c/sicken/files/sicken/speech"
run "touch /c/sicken/logs/sicken-concurrent.log"

print "Installation complete. Run the initialise_rabbitmq.bat file and restart your computer to start using Sicken."
read nothing