#! /usr/bin/bash



echo "would you like to change the local host to a different Ip address? give answer y/n"
read var1


if [ $var1 == "y" ]
then 
    echo "please provide the IP address"
    read Ip

    issuer="http://${Ip}:8080/auth/realms/n5geh"
    auth_uri="http://${Ip}:8080/auth/realms/n5geh/protocol/openid-connect/auth"
    redirect_uris="http://${Ip}:8090/*"

    jq '.web.issuer="'${issuer}'"' entirety/client_secrets.json > tmp.$$.json && mv tmp.$$.json entirety/client_secrets.json
    jq '.web.auth_uri="'${auth_uri}'"' entirety/client_secrets.json > tmp.$$.json && mv tmp.$$.json entirety/client_secrets.json
    jq '.web.redirect_uris=["'${redirect_uris}'"]' entirety/client_secrets.json > tmp.$$.json && mv tmp.$$.json entirety/client_secrets.json

    #cat client_secrets.json | jq '.web.auth_uri = $v' --arg v ${auth_uri} | sponge client_secrets.json
    echo " "
    echo your Ip address has changed from localhost to $Ip
    
fi 
echo " " 
echo "you can enter the keycloak now" 
echo "login to the keycloak go to down down menu 'Select reamlm' -> n5geh ->clients -> device-wizard -> Credentials  "

echo "re generate the 'Secret', copy  and then enter the secret key" 
read secret 

jq '.web.client_secret="'${secret}'"' entirety/client_secrets.json > tmp.$$.json && mv tmp.$$.json entirety/client_secrets.json

echo " "

