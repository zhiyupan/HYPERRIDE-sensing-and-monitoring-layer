[![ENTIRETY Banner](documentation/images/Entirety-logo.png)](https://www.n5geh.de)
# ENTIRETY - Semantic Provisioning and Governing IoT Devices in Smart Energy Domain

Repository for Device provisioning application so called ENTIRETY.

## Content

-  [Installation of Entirety ](#installation-of-entirety)
-  [GUI Application Overview](#gui-application-overview)


## Installation of Entirety
This GUI prepared to provision and register IoT devices into the N5GEH project platform (https://n5geh.de/) .  This interface includes a data model and provides information for the user to register IoT devices. This interface hosts a list of the template that made for classes of the data model and provides an easy way to validate instances of classes into the platform.

  **Requirements**
   ```yaml
npm (verion >= 3.5.2)
python (version =3.6.8)
```

  **Installation**

Install all packages for the front end part 
```bash
$ cd static
$ npm install
```

Install all packages for the back end part 
```bash
$ pip install -r requirements.txt
```
  **Configuration**

Here is an example of configuration file for the Entirety:
```json
{
  "device_idm": {
    "server": "http://keycloak:8080/auth/",
    "username": "device_wizard",
    "password": "password",
    "realm_name": "n5geh_devices"
  },
  "fiware": {
    "orion": "http://orion:1026",
    "quantumleap": "http://quantumleap:8668",
    "iotagent": "http://iot-agent:4041"
  },
  "datamodel": {
    "ngsi2": "/data/datamodel/NGSI2",
    "ngsi-ld": "/data/datamodel/NGSI-LD",
    "classes": "/data/datamodel/classes"
  },
  "idm": {
    "account_url": "http://localhost:8080/auth/realms/n5geh/account",
    "logout_link": "http://localhost:8080/auth/realms/n5geh/protocol/openid-connect/logout?referrer=flask-app&redirect_uri=http%3A%2F%2Flocalhost%3A8090%2Fdashboard"
  }
}
```
* device_idm - data for connecting to Keycloak server
* fiware - configuration of FIWARE services
* datamodel - pathes to Datamodel templates
* idm - endpoints for authentication and authorization

## GUI Application Overview

This document describes the Entirety Graphical User Interface (GUI) Application. The GUI is a Web Application which is first installed and then runs on the server. the application provides a convenient way to perform setup and demonstrate device registration features from within a standard Web application environment.

### Features
The GUI is a Web Split Pane Application. In general, features appear in the left pane and graphical content appears in the right pane. A separate, tabbed dialogue type interface supports board setup operations. The device demonstrates list of properties (with validation feed back) with dropdown menus, edit boxes and date table as the registration control. The registered devices Panel demonstrates a  selection control with the name of devices to filter and a table to present a list of already existing of this type of device in a table. 

### Opening Screen

 Execute (Run) the GUI as written in the instruction. You will see the initial HOME Screen which contains username and password options for authentication. 
 <img src="documentation/images/IDM.png" width=850>


###  Entirety Menus

This menu provides the usual {register , Open..., } options. In this application you use this menu and the associated Dialogs to register and modify IoT devices. Example; Assuming that you have registered the desired device type into application in the GUI, you can use the register menu to save the data to the platform. When you again run the GUI you can use the registered device to retrieve the already existing data to the GUI. 

 <img src="documentation/images/Menu.png" width=850> 
 
####  Device Menu
This is the usual Web Edit Interface. 
You use this dialog to set properties of your device and open channel between the GUI Application and the platform. This will test communication and serve to registration  using the API (binary) Command Interface.  By selecting "+ IoT Agent" in the left pane, the right pane list of device types will be shown. The user can select appreciated type of device from this dropdown menu and see list of properties belong to the device type by pressing register Button.

 <img src="documentation/images/RegisterMenu.png" width=850> 
 
The Mandatory properties can not be left empty and you will receive feedback about validation of provided information. A list of properties for PMU are presented in the image. 
 
  <img src="documentation/images/registerProperties.png" width=850> 

####  Registered Devices Menu
This is the usual Web View Interface. This menu is currently used by the GUI application to reterive the existing devices. By selecting "Registered devices" in the left pane, in the right pane, user is able to filter according to the specific type of device from dropdown and decide how many row data wants to see. The result will be shown in the table of right pane.

  <img src="documentation/images/showEntities.png" width=850> 

# License

- [MIT-License](LICENSE)

# Copyright

2020, Technische Universität Dresden

# Contact



[<img src="https://cn.ifn.et.tu-dresden.de/wp-content/uploads/2019/01/ComNets_MZ_RGB_Subline_en.png" alt="ComNets_Logo" width="168px"/>](https://cn.ifn.et.tu-dresden.de)
[![TU_DRESDEN_Logo](https://tu-dresden.de/++theme++tud.theme.webcms2/img/tud-logo.svg)](https://tu-dresden.de/)

- [Ilya Sychev](https://cn.ifn.et.tu-dresden.de/chair/staff/ilya-sychev/)

[The Deutsche Telekom Chair of Communication Networks](https://cn.ifn.et.tu-dresden.de/)

[Technische Universität Dresden, Germany](https://tu-dresden.de/)

# Acknowledgement
<img src="https://www.ebc.eonerc.rwth-aachen.de/global/show_picture.asp?mod=w%3d474%26h%3d%26gray%3d%26neg%3d%26mirror%3d%26flip%3d%26rleft%3d%26rright%3d%26r180%3d%26crop%3d%26id%3daaaaaaaaaayxgwf&id=aaaaaaaaaayxgwf" width="250">

We gratefully acknowledge the financial support provided by the BMWi (Federal Ministry for Economic Affairs and Energy), promotional reference 03ET1561A/B/C

