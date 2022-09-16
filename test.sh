#! /usr/bin/bash

jq '.clients|.[0].redirectUris|.[]' n5geh-realm.json

jq '.clients.redirectUris|.[]' n5geh-realm.json


jq '.web.issuer' client_secrets.json 
jq '.web.auth_uri' client_secrets.json 
jq '.web.redirect_uris|.[]' client_secrets.json


#jq '.clients|.[0].redirectUris="0.0.0.0"' n5geh-realm.json > tmp.$$.json && mv tmp.$$.json n5geh-realm_new.json
