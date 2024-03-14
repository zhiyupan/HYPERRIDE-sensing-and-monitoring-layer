#! /usr/bin/bash

echo "you can enter the keycloak now"
echo "login to the keycloak go to drop down menu 'Select reamlm' -> N5geh ->clients -> device-wizard -> Credentials  "
echo " "
echo "re generate the 'Secret', copy  and then enter the secret key"
read secret_entirety

jq '.web.client_secret="'${secret_entirety}'"' entirety/client_secrets.json > tmp.$$.json && mv tmp.$$.json entirety/client_secrets.json
echo "your client secret of device-wizard has been change to the secret key you entered"
echo " "
    
echo "Now repeat the process for the mqtt-broker" 
echo "Go to the drop down menu 'Select reamlm' -> N5geh_devices ->clients -> mqtt_broker -> Credentials"
echo "re generate the 'Secret', copy and then enter the secret key"
read secret_mqtt
line_string="auth_opt_oauth_client_secret ${secret_mqtt}"
line_number=`awk '/auth_opt_oauth_client_secret/{ print NR;}' mosquitto/conf.d/go-auth.conf`
sed  -i "${line_number}s/.*/$line_string/" mosquitto/conf.d/go-auth.conf

echo "your client secrets mqtt broker has been change to the secret key you entered"
echo " "
echo "Updating......... "
echo "Please wait for the update to finish"
sudo ./services secrets_update
