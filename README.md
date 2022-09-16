# N5GEH tutorial for ENTIRETY 

This is a tutorial of how to use ENTIRETY for device provisioning for the N5GEH Cloud Platform. To demonstrate the work of the components everything is configured locally. To start using the tutorial it is necessary to install Pre-requisites.

## Pre-requisites 
* Docker engine
* Docker compose

## Manual

### Start
Open the terminal and then type the command:
```bash
./services start
```
This command starts all services from the docker-compose file and run setup for the demo.

### Set of services

The picture below shows the set of services for the tutorial.
<p align="center">
<img src="documentation/images/Entirety-diagram.png " width=300>
</p>

### List of the service

Here is the list of the services:
- [KeyCloak](http://localhost:8080) with login: **admin** and password: **Pa55w0rd**
- [Entirety](http://localhost:8090) with login: **n5geh** and password: **n5geh**
- [Grafana](http://localhost:3003) with login: **admin** and password: **admin**

### Initializing the services

To start using services it is MANDATORY to provide a CLIENT_SECRETS from the Keycloak Identity Manager.

### Local host change

```bash
would you like to change the local host to a different Ip address? give answer y/n
```

If you are not running the project from the local device than type "y" and then type the ip address,
else please any key and the default "localhost" will remain as it is.

If a change is made in the localhost then change in the Devide-Wizard Settings has to be made as well:

<img src="documentation/images/localhost_change.png" width=900>

#### Initializing services

Login to the Keycloak Admin dashboard via [KeyCloak](http://localhost:8080) with login: **admin** and password: **Pa55w0rd**.

<img src="documentation/images/Log in to Keycloak.png" width=900>

#### Update client secrets for Entirety

Regenerate the Client Secret for Entirety.

<img src="documentation/images/N5GEH_realm_clients.png" width=900>
<img src="documentation/images/N5GEH_realm_device-wizard_generate_secret.png" width=900>

Copy and past it in the bash after this message.

```bash
login to the keycloak go to down down menu 'Select reamlm' -> n5geh ->clients -> device-wizard -> Credentials re generate the 'Secret', copy  and then enter the secret key

```

#### Update client secrets for MQTT Broker

Regenerate the Client Secret for MQTT Broker and rewrite it in the configuration file.

<img src="documentation/images/Switch_realm.png" width=900>
<img src="documentation/images/N5GEH_device_realm_clients.png" width=900>
<img src="documentation/images/N5GEH_device_realm_mqtt_broker_generate_secret.png" width=900>
<img src="documentation/images/Edit_Mqtt_broker_config.png" width=900>
<img src="documentation/images/Edit_Mqtt_broker_config_paste_secret.png" width=900>


#### Restart services with updated keys

To apply changes it is necessary to restart docker containers with services. 

```bash
./services secrets_update
```

## Entirety

### Login page

Now, the ENTIRETY service should be available via this [Entirety](http://localhost:8090) with login: **n5geh** and password: **n5geh**.

<img src="documentation/images/Log in to Entirety.png" width=900>

### Dashboard
Here is a ENTIRETY Dashboard.

<img src="documentation/images/Entirety_dashboard.png" width=900>

### Initialize classes
<img src="documentation/images/Entirety_dashboard_classes.png" width=900>

### Initialize subscriptions
<img src="documentation/images/Entirety_dashboard_classes_subscriptions.png" width=900>

### User preferences

<img src="documentation/images/Entirety_user_preferences.png" width=900>
<img src="documentation/images/Entirety_keycloak_user.png" width=900>

### Add/Remove device

Entirety supports two type of Datamodel definition: NGSIv2 and NGSI-LD.
Because IoT Agent currently does not support NGSI-LD than in this tutorial we are showing an example with NGSIv2.

Here is definition of the Meter in the Datamodel:
```javascript
{
  "base_template": "base/Device.json",
  "device_id": {
    "name": "device_id",
    "label": "Device Id",
    "required": "true",
    "prefix": "urn:ngsi-ld:Meter:"
  },
  "entity_name": "",
  "entity_type": "Meter",
  "attributes": [
    {
      "object_id": "nam",
      "name": "name",
      "type": "String"
    },
    {
      "object_id": "lis",
      "name": "listening",
      "type": "String"
    },
    {
      "object_id": "sam",
      "name": "sampleRate",
      "type": "String"
    },
    {
      "object_id": "wri",
      "name": "writable",
      "type": "String"
    },
    {
      "object_id": "saI",
      "name": "sampleInterval",
      "type": "String"
    },
    {
      "object_id": "loI",
      "name": "loggingInterval",
      "type": "String"
    }
  ],
  "commands": [],
  "static_attributes": [
    {
      "name": "subCategory",
      "label": "Sub Category",
      "type": "Property",
      "value": "GridRelated",
      "required": "true"
    },
    {
      "name": "hasChannel",
      "label": "Channel",
      "type": "Relationship",
      "value": "",
      "query": "Channel",
      "required": "true"
    },
    {
      "name": "isMeasuredIn",
      "type": "Relationship",
      "label": "Measure",
      "value": "",
      "query": "Measurement",
      "required": "true"
    }
  ]
}
```
And also definition of Device (base object for all devices).
```javascript
{
  "protocol": "",
  "timezone": "",
  "attributes": [
    {
      "object_id": "crA",
      "name": "createdAt",
      "type": "datetime"
    },
    {
      "object_id": "moA",
      "name": "modifiedAt",
      "type": "datetime"
    },
    {
      "object_id": "cat",
      "name": "category",
      "type": "String"
    },
        {
      "object_id": "dvP",
      "name": "voltage_p",
      "type": "Integer"
    },
    {
      "object_id": "dvM",
      "name": "voltage_m",
      "type": "Integer"
    },
    {
      "object_id": "dc1P",
      "name": "current1P",
      "type": "Integer"
    },
    {
      "object_id": "dc1M",
      "name": "current1m",
      "type": "Integer"
    },
    {
      "object_id": "dc2P",
      "name": "current2P",
      "type": "Integer"
    },
    {
      "object_id": "dc2M",
      "name": "current2M",
      "type": "Integer"
    },
    {
      "object_id": "dc3P",
      "name": "current3p",
      "type": "Integer"
    }
    {
      "object_id": "dc3M",
      "name": "current3m",
      "type": "Integer"
    },
    {
      "object_id": "dc4P",
      "name": "current4p",
      "type": "Integer"
    },
    {
      "object_id": "dc4M",
      "name": "current4m",
      "type": "Integer"
    },
    {
      "object_id": "ipA",
      "name": "ipAddress",
      "type": "String"
    },
    {
      "object_id": "ipA",
      "name": "ipAddress",
      "type": "String"
    },
    {
      "object_id": "coA",
      "name": "controlAsset",
      "type": "String"
    },
    {
      "object_id": "enV",
      "name": "entityVersion",
      "type": "String"
    },
    {
      "object_id": "seN",
      "name": "serialNumber",
      "type": "String"
    },
    {
      "object_id": "suN",
      "name": "supplierName",
      "type": "String"
    },
    {
      "object_id": "des",
      "name": "description",
      "type": "String"
    },
    {
      "object_id": "sou",
      "name": "source",
      "type": "String"
    },
    {
      "object_id": "daP",
      "name": "dataProvider",
      "type": "String"
    }
  ],
  "static_attributes": [
    {
      "name": "hasState",
      "type": "Relationship",
      "label": "State",
      "query": "State",
      "required": "true"
    },
    {
      "name": "controlsProperty",
      "type": "Relationship",
      "label": "Property",
      "query": "Property",
      "required": "true"
    },
    {
      "name": "isMeasuredIn",
      "type": "Relationship",
      "label": "Measurement",
      "query": "Measurement",
      "required": "true"
    },
    {
      "name": "hasCommand",
      "type": "Relationship",
      "label": "Command",
      "query": "Command",
      "required": "true"
    },
    {
      "name": "hasFunction",
      "type": "Relationship",
      "label": "Function",
      "query": "Function",
      "required": "true"
    },
    {
      "name": "conssistOf",
      "type": "Relationship",
      "label": "Consist of",
      "query": "",
      "required": "false"
    }
  ]
}
```
Entirety uses this data to prepare the web form and generate final object for the device.
Here is an example of registering the device.

<img src="documentation/images/Entirety_iot_add_select.png" width=900>
<img src="documentation/images/Entirety_iot_add_form.png" width=900>
<img src="documentation/images/Entirety_iot_add_success.png" width=900>
<img src="documentation/images/Entirety_iot_list.png" width=900>
<img src="documentation/images/Entirety_iot_list_mqtt_topic.png" width=900>


### Services
<img src="documentation/images/Entirety_iot_service_list.png" width=900>

### Notifications
<img src="documentation/images/Entirety_notifications.png" width=900>

### Crate DB Database
New table will be added as shown
<img src="documentation/images/cratedb_table_added.png" 
width=900>


### Send a MQTT message

According to registered device:

* Username **urn:ngsi-ld:meter:meter001**
* Password **secret**
* Topic **/n5geh3c4d3da22af22bb6/urn:ngsi-ld:Meter:meter001/attrs**

In this tutorial we are using IoT Agent UL version and uploading data from CSV file.

```python
#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pandas as pd
import time

df = pd.read_excel('D:\switch_gear\Switchgear1.xls')
df["Timestamp"]=pd.to_datetime(df.Timestamp)
col_name=[]

for col in df.columns:
    col_name.append (col)
col_name = col_name[:-2]

for index, row in df.iterrows():
    client = mqtt.Client()
    client.username_pw_set("urn:ngsi-ld:meter:meter001", "secret")
    client.connect("137.226.248.224", 1883, 60)
    client.publish("/n5geh3c4d3da22af22bb6/urn:ngsi-ld:Meter:meter001/attrs", "dvP|{}|dvM|{}|dc1P|{}|dc1M|{}|dc2P|{}|dc2M|{}|dc3P|{}|dc3M|{}|dc4P|{}|dc4M|{}".format(
        int(row[col_name[1]]),
        int(row[col_name[2]]),
        int(row[col_name[3]]),
        int(row[col_name[4]]),
        int(row[col_name[5]]),
        int(row[col_name[6]]),
        int(row[col_name[7]]),
        int(row[col_name[8]]),
        int(row[col_name[9]]),
        int(row[col_name[10]]),
    ));
    client.disconnect();
    count= index+1
    print (count," row inserted in the table")
    time.sleep(3)
    if count == 10:
        break
```

#### Data

The data goes to the CrateDB and stores in the table 'mtopeniot.etmeter'.

<img src="documentation/images/data_table.JPG" 
width=900>

### Grafana
Put the parameters in accordingly in the query table:

<img src="documentation/images/grafana_query.PNG" 
width=900>

And the data can be visualised as shown below:
<img src="documentation/images/grafana_graph.PNG" 
width=900>

### Stop

To stop the tutorials please run following command:

```bash
./services stop
```
