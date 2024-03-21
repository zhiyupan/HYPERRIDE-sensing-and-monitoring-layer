#! /usr/bin/bash


echo " "
echo "would you like to change the local host to a different Ip address?"
echo "If yes press 'y'" 
echo "If No press 'n' "
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
    jq '.clients[0].redirectUris=["'${redirect_uris}'"]' keycloak/n5geh-realm.json > tmp.$$.json && mv tmp.$$.json keycloak/n5geh-realm.json

    #cat client_secrets.json | jq '.web.auth_uri = $v' --arg v ${auth_uri} | sponge client_secrets.json
    echo " "
    echo your Ip address has changed from localhost to $Ip
    echo " "
    echo "The Setup is restarting..."
    echo "Please wait for the project to restart" 
else
    echo "your localhost stays as default or previously change"   
    echo " "
fi 


