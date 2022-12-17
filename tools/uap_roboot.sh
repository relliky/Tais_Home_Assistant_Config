#!/bin/bash

#######################################################################
# A simple script for remotely rebooting a Ubiquiti UniFi access point
#
# Requires bash and sshpass (https://sourceforge.net/projects/sshpass/)
# which should be available via dnf, yum, or apt on your *nix distro.
#
# This can be done by running "apk add --update --no-cache sshpass" in 
# the terminal addon.
#
# USAGE
# Update the user-configurable settings below, then run ./uap_reboot.sh from
# the command line. To reboot on a schedule, create a cronjob such as:
# 45 3 * * * /usr/local/bin/unifi-linux-utils/uap_reboot.sh > /dev/null 2>&1 #Reboot UniFi APs
# The above example will reboot the UniFi access point(s) every morning at 3:45 AM.
#
# Way to be called by Home Assistant - using shell_script to ssh to terminal addon and run commands
# https://community.home-assistant.io/t/execute-bash-script-dont-find-sshpass/175604/10
#
#######################################################################

# Source username/password from secrets.sh

script_dir="$( dirname -- "${BASH_SOURCE[0]}"; )"
secret_path=$script_dir"/../secrets.sh"
source $secret_path

known_hosts_file=/dev/null
# USER-CONFIGURABLE SETTINGS
              #1F            #2F            #0F
uap_list=(192.168.1.24   192.168.1.23   192.168.1.1 )

# SHOULDN'T NEED TO CHANGE ANYTHING PAST HERE
for i in "${uap_list[@]}"
do
	echo "Rebooting UniFi access point at $i..."
	if sshpass -p $password ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=$known_hosts_file -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa $username"@$i" reboot; then
    echo "Access point at $i rebooted!" 1>&2
	else
    echo "Could not reboot access point at $i." 1>&2
	fi
	sleep 300
done
exit 0